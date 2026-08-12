# Gmail skill — setup & security model

## Why this instead of Composio / a connector

A connector like Composio works by holding an OAuth token for your account on
their servers (often with the broad `https://mail.google.com/` scope — full
read/write/send/delete). This skill keeps everything on your machine: the app
password lives in your macOS Keychain, and the only network calls are direct,
TLS-encrypted connections to Google's own IMAP/SMTP servers.

## Prerequisites

1. **2-Step Verification** must be ON for the Google account.
   https://myaccount.google.com/security
2. **Create an app password:** https://myaccount.google.com/apppasswords
   - Name it e.g. "claude-gmail-skill". Google shows a 16-character code.
3. **Enable IMAP:** Gmail → Settings (gear) → "See all settings" →
   "Forwarding and POP/IMAP" → "Enable IMAP" → Save.

## Store the credential

Run interactively, from this skill's directory, so the password is typed
locally and never pasted into a chat:

```
python3 scripts/gmail.py setup
```

- Address goes to `~/.config/gmail-skill/config.json` (chmod 600, not secret).
- Password goes to the macOS Keychain under service `gmail-skill`,
  account = your email. Inspect/remove it anytime in **Keychain Access**, or:

  ```
  security find-generic-password -s gmail-skill -a you@gmail.com    # metadata
  security delete-generic-password -s gmail-skill -a you@gmail.com  # revoke locally
  ```

To revoke access entirely, delete the app password at
https://myaccount.google.com/apppasswords — it instantly stops working.

## Credential resolution order

1. `GMAIL_ADDRESS` + `GMAIL_APP_PASSWORD` env vars (useful on Linux/CI where
   there is no Keychain).
2. macOS Keychain (written by `setup`).
3. `~/.config/gmail-skill/config.json` supplies the address only.

## Limitations vs. the Gmail API

- App-password access is IMAP/SMTP, so there's no labels/threads REST API,
  push notifications, or fine-grained scopes — it's effectively full-mailbox
  access. For least-privilege (`gmail.readonly`) you'd need a self-hosted
  OAuth client and the Gmail REST API instead.
- Google Workspace admins can disable app passwords org-wide; if so, this
  path won't be available and OAuth is the only option.

## Multi-device note

This skill's files (`SKILL.md`, `scripts/gmail.py`, this reference) live in
this project's `.claude/skills/gmail/` so they travel with the Cowork folder
to any device. The Keychain entry and `~/.config/gmail-skill/config.json` are
per-machine and do **not** sync — run `setup` once on each new device.
