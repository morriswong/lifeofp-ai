#!/usr/bin/env python3
"""Self-hosted Gmail access using your own Google account (app password).

No third-party connector. Talks directly to Gmail over IMAP (read) and
SMTP (send) using Python's standard library only.

Credentials are resolved in this order:
  1. Environment variables  GMAIL_ADDRESS / GMAIL_APP_PASSWORD
  2. macOS Keychain         (written by `gmail.py setup`)
  3. ~/.config/gmail-skill/config.json  (address only; never the password)

The app password is NEVER printed and NEVER stored in plaintext by this tool.

Usage:
  gmail.py setup
  gmail.py search "from:foo@bar.com has:attachment" [--limit 10] [--json]
  gmail.py read <uid> [--html] [--mailbox "[Gmail]/All Mail"]
  gmail.py attachments <uid> [--list] [--save DIR]
  gmail.py send --to a@b.com --subject "Hi" --body "text" [--attach path ...] [--cc ...] [--bcc ...]
"""
import argparse
import getpass
import imaplib
import json
import os
import smtplib
import ssl
import subprocess
import sys
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import getaddresses

IMAP_HOST = "imap.gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
# Verified TLS: imaplib/smtplib *_SSL classes fall back to an UNVERIFIED
# stdlib context when none is passed (check_hostname=False, CERT_NONE), so we
# must supply a verifying context explicitly to prevent MITM credential theft.
SSL_CTX = ssl.create_default_context()
# Socket timeout (seconds) so a stalled peer can't hang the CLI indefinitely.
TIMEOUT = 30
KEYCHAIN_SERVICE = "gmail-skill"
CONFIG_DIR = os.path.expanduser("~/.config/gmail-skill")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_MAILBOX = "[Gmail]/All Mail"


# ----------------------------- credentials -----------------------------

def _config_address():
    try:
        with open(CONFIG_PATH) as fh:
            return json.load(fh).get("address")
    except (OSError, ValueError):
        return None


def _keychain_password(address):
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-a", address,
             "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_credentials():
    address = os.environ.get("GMAIL_ADDRESS") or _config_address()
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if password is None and address:
        password = _keychain_password(address)
    if not address or not password:
        sys.exit("No credentials. Run `gmail.py setup` first, or set "
                 "GMAIL_ADDRESS and GMAIL_APP_PASSWORD env vars.")
    return address, password


def cmd_setup(args):
    print("Gmail skill setup — stores your app password in the macOS Keychain.\n")
    address = args.address
    if not address:
        if not sys.stdin.isatty():
            sys.exit("Non-interactive shell: pass --address you@gmail.com "
                     "(and set GMAIL_APP_PASSWORD), or run this in a real "
                     "terminal window.")
        address = input("Gmail address: ").strip()
    if not address:
        sys.exit("Address is required.")
    pw = os.environ.get("GMAIL_APP_PASSWORD")
    if pw is None:
        if not sys.stdin.isatty():
            sys.exit("Non-interactive shell: set GMAIL_APP_PASSWORD in the "
                     "environment, or run setup in a real terminal window so "
                     "the hidden password prompt works.")
        pw = getpass.getpass("App password (16 chars, input hidden): ")
    pw = pw.replace(" ", "").strip()
    if not pw:
        sys.exit("App password is required.")
    # Store password in Keychain (-U updates if it already exists). We pass
    # `-w` with NO value and feed the password via stdin (twice: the tool
    # prompts for password + confirmation) so the secret never appears in the
    # process argv, where same-user `ps`/audit tooling could read it.
    try:
        subprocess.run(
            ["security", "add-generic-password", "-a", address,
             "-s", KEYCHAIN_SERVICE, "-U", "-w"],
            input="%s\n%s\n" % (pw, pw),
            check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("`security` not found — Keychain storage is macOS only. "
                 "Use GMAIL_ADDRESS / GMAIL_APP_PASSWORD env vars instead.")
    except subprocess.CalledProcessError as e:
        sys.exit("Keychain write failed: " + (e.stderr or str(e)))
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as fh:
        json.dump({"address": address}, fh)
    os.chmod(CONFIG_PATH, 0o600)
    # Verify by logging in.
    try:
        M = imaplib.IMAP4_SSL(IMAP_HOST, ssl_context=SSL_CTX, timeout=TIMEOUT)
        M.login(address, pw)
        M.logout()
    except imaplib.IMAP4.error as e:
        sys.exit("Stored, but login test FAILED: %s\nCheck the app password / "
                 "that IMAP is enabled in Gmail settings." % e)
    print("\nSaved to Keychain and login verified for", address)


# ----------------------------- imap helpers -----------------------------

def _decode(value):
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def imap_connect():
    address, password = load_credentials()
    M = imaplib.IMAP4_SSL(IMAP_HOST, ssl_context=SSL_CTX, timeout=TIMEOUT)
    try:
        M.login(address, password)
    except imaplib.IMAP4.error as e:
        sys.exit("IMAP login failed: %s\nVerify the app password and that IMAP "
                 "is enabled (Gmail > Settings > Forwarding and POP/IMAP)." % e)
    return M


def _select(M, mailbox, readonly=True):
    typ, _ = M.select('"%s"' % mailbox, readonly=readonly)
    if typ != "OK":
        sys.exit("Could not open mailbox: %s" % mailbox)


def _fetch_header(M, uid):
    typ, data = M.uid("FETCH", uid,
                      "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])")
    if typ != "OK" or not data or data[0] is None:
        return {}
    raw = data[0][1]
    msg = message_from_bytes(raw)
    return {
        "from": _decode(msg.get("From")),
        "to": _decode(msg.get("To")),
        "subject": _decode(msg.get("Subject")),
        "date": _decode(msg.get("Date")),
    }


def cmd_search(args):
    M = imap_connect()
    try:
        _select(M, args.mailbox, readonly=True)
        # X-GM-RAW lets us use full Gmail search syntax (same as the web UI).
        # Send the query as a CHARSET UTF-8 IMAP literal (M.literal) rather than
        # interpolating into a quoted string: this avoids quote/criteria
        # injection and supports non-ASCII (e.g. Chinese) queries, which would
        # otherwise raise UnicodeEncodeError under imaplib's ASCII encoding.
        M.literal = args.query.encode("utf-8")
        typ, data = M.uid("SEARCH", "CHARSET", "UTF-8", "X-GM-RAW")
        if typ != "OK":
            sys.exit("Search failed.")
        uids = (data[0] or b"").split()
        uids = uids[-args.limit:][::-1] if args.limit > 0 else []  # recent first
        results = []
        for uid in uids:
            uid_s = uid.decode()
            hdr = _fetch_header(M, uid_s)
            hdr["uid"] = uid_s
            results.append(hdr)
    finally:
        M.logout()
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No matching messages.")
        for r in results:
            print("uid %s | %s" % (r["uid"], r.get("date", "")))
            print("  from: %s" % r.get("from", ""))
            print("  subj: %s\n" % r.get("subject", ""))


def _walk_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fn = part.get_filename()
        disp = (part.get("Content-Disposition") or "").lower()
        if fn or "attachment" in disp:
            yield part, _decode(fn) or "unnamed"


def _load_message(M, uid, mailbox):
    _select(M, mailbox, readonly=True)
    typ, data = M.uid("FETCH", uid, "(BODY.PEEK[])")
    if typ != "OK" or not data or data[0] is None:
        sys.exit("Message uid %s not found in %s." % (uid, mailbox))
    return message_from_bytes(data[0][1])


def cmd_read(args):
    M = imap_connect()
    try:
        msg = _load_message(M, args.uid, args.mailbox)
    finally:
        M.logout()
    want = "html" if args.html else "plain"

    def _text(part):
        raw = part.get_payload(decode=True)
        if raw is None:
            return ""
        return raw.decode(part.get_content_charset() or "utf-8", "replace")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/%s" % want:
                body = _text(part)
                break
        if not body:  # fall back to whatever text we can find
            for part in msg.walk():
                if part.get_content_maintype() == "text":
                    body = _text(part)
                    break
    else:
        body = _text(msg)
    atts = [name for _, name in _walk_attachments(msg)]
    print("From:    %s" % _decode(msg.get("From")))
    print("To:      %s" % _decode(msg.get("To")))
    print("Date:    %s" % _decode(msg.get("Date")))
    print("Subject: %s" % _decode(msg.get("Subject")))
    if atts:
        print("Attachments: %s" % ", ".join(atts))
    print("\n" + body.strip())


def cmd_attachments(args):
    M = imap_connect()
    try:
        msg = _load_message(M, args.uid, args.mailbox)
    finally:
        M.logout()
    found = list(_walk_attachments(msg))
    if not found:
        print("No attachments on uid %s." % args.uid)
        return
    if args.list or not args.save:
        for _, name in found:
            print(name)
        if not args.save:
            return
    os.makedirs(args.save, exist_ok=True)
    used = set()
    for part, name in found:
        safe = os.path.basename(name) or "unnamed"
        # De-duplicate so same-named attachments don't silently overwrite.
        base, ext = os.path.splitext(safe)
        n = 1
        while safe in used:
            safe = "%s-%d%s" % (base, n, ext)
            n += 1
        used.add(safe)
        path = os.path.join(args.save, safe)
        with open(path, "wb") as fh:
            fh.write(part.get_payload(decode=True) or b"")
        print("saved: %s" % path)


def cmd_send(args):
    address, password = load_credentials()
    msg = EmailMessage()
    msg["From"] = address
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    msg["Subject"] = args.subject
    msg.set_content(args.body)
    for path in args.attach or []:
        with open(path, "rb") as fh:
            data = fh.read()
        msg.add_attachment(data, maintype="application", subtype="octet-stream",
                           filename=os.path.basename(path))
    # getaddresses parses comma-separated RFC-5322 lists correctly, so a
    # display name containing a comma (e.g. '"Bar, Foo" <a@b.com>') is not
    # split into garbage addresses the way a naive str.split(",") would.
    recipients = [addr for _, addr in
                  getaddresses([args.to, args.cc or "", args.bcc or ""]) if addr]
    if not recipients:
        sys.exit("No valid recipient address parsed from --to/--cc/--bcc.")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=SSL_CTX, timeout=TIMEOUT) as s:
        s.login(address, password)
        s.send_message(msg, from_addr=address, to_addrs=recipients)
    print("Sent to %s" % ", ".join(recipients))


# ----------------------------- cli -----------------------------

def main():
    p = argparse.ArgumentParser(description="Self-hosted Gmail via your own account.")
    sub = p.add_subparsers(dest="cmd", required=True)

    su = sub.add_parser("setup", help="Store app password in macOS Keychain.")
    su.add_argument("--address", help="Gmail address (skips the prompt).")

    s = sub.add_parser("search", help="Search with Gmail query syntax.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--mailbox", default=DEFAULT_MAILBOX)
    s.add_argument("--json", action="store_true")

    r = sub.add_parser("read", help="Read a message by uid.")
    r.add_argument("uid")
    r.add_argument("--html", action="store_true")
    r.add_argument("--mailbox", default=DEFAULT_MAILBOX)

    a = sub.add_parser("attachments", help="List or download attachments of a uid.")
    a.add_argument("uid")
    a.add_argument("--list", action="store_true")
    a.add_argument("--save", help="Directory to save attachments into.")
    a.add_argument("--mailbox", default=DEFAULT_MAILBOX)

    sd = sub.add_parser("send", help="Send an email.")
    sd.add_argument("--to", required=True)
    sd.add_argument("--subject", required=True)
    sd.add_argument("--body", required=True)
    sd.add_argument("--cc")
    sd.add_argument("--bcc")
    sd.add_argument("--attach", nargs="*")

    args = p.parse_args()
    {"setup": cmd_setup, "search": cmd_search, "read": cmd_read,
     "attachments": cmd_attachments, "send": cmd_send}[args.cmd](args)


if __name__ == "__main__":
    main()
