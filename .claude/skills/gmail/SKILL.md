---
name: gmail
description: Access your own Gmail account directly over IMAP/SMTP using an app password — no third-party connector (Composio etc.). Search, read, download attachments, and send mail. Use when the user wants to read/search/send their own Gmail, pull an email or attachment, or set up self-hosted Gmail access. Credentials live in the macOS Keychain, never in chat.
---

# Gmail (self-hosted, your own account)

Direct Gmail access via Python stdlib only (`imaplib`/`smtplib`/`email`). No
pip installs, no external service holding your token. Auth is a Google
**app password** stored in the macOS Keychain.

Script: `scripts/gmail.py` (run with the system `python3`).

Project-scoped copy: this skill lives in this Cowork project's `.claude/skills/`
so it travels with the project across devices. Each device still needs its own
one-time `setup` run — the app password lives in that machine's Keychain and
never syncs.

## First-time setup (once per machine)

The user must have 2-Step Verification on, then create an app password at
https://myaccount.google.com/apppasswords and enable IMAP in
Gmail → Settings → Forwarding and POP/IMAP.

Then THEY run setup interactively (so the password never enters the chat):

```
python3 scripts/gmail.py setup
```

This stores the password in the Keychain (service `gmail-skill`) and the
address in `~/.config/gmail-skill/config.json`, then verifies login.

Never ask the user to paste the app password into the conversation. If setup
hasn't run, instruct them to run the command above themselves (e.g. via the
`!` prefix in Claude Code so it runs in their session).

## Commands

Search uses **full Gmail query syntax** (same as the web search box):

```
python3 scripts/gmail.py search "from:foo@bar.com has:attachment newer_than:30d" --limit 10
python3 scripts/gmail.py search "subject:invoice" --json        # machine-readable
```

Read a message (use the `uid` from search; default mailbox is All Mail):

```
python3 scripts/gmail.py read <uid>
python3 scripts/gmail.py read <uid> --html
```

List / download attachments:

```
python3 scripts/gmail.py attachments <uid> --list
python3 scripts/gmail.py attachments <uid> --save ./out
```

Send mail (From is your account automatically):

```
python3 scripts/gmail.py send --to a@b.com --subject "Hi" --body "Text here"
python3 scripts/gmail.py send --to a@b.com --cc c@d.com --subject "Docs" \
    --body "See attached" --attach ./file.pdf
```

## Notes & gotchas

- `uid` values are scoped to a mailbox. `read`/`attachments` default to
  `[Gmail]/All Mail` to match what `search` returns. Pass `--mailbox INBOX`
  to operate elsewhere.
- Reads use `BODY.PEEK[]`, so opening a message does **not** mark it read.
- Search supports non-ASCII queries (e.g. Chinese): the query is sent as a
  CHARSET UTF-8 IMAP literal, so quotes and Unicode are handled safely.
- Credentials resolve from env vars `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD`
  first (handy on non-macOS / CI), then Keychain, then the config file.
- See `references/setup.md` for the full app-password walkthrough and
  security model.
