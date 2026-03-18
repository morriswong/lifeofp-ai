# Claude Code + ttyd + Chrome: Quick Start Guide

Share a Claude Code terminal session via browser that can control your Chrome.

## Prerequisites

- macOS
- [ttyd](https://github.com/tsl0922/ttyd) (`brew install ttyd`)
- Claude Code CLI
- Google Chrome

## Steps

### 1. Fully quit Chrome

**Cmd+Q** Chrome completely. If Chrome is still running, the debug flag won't take effect and it will just open a new tab in the existing session.

### 2. Relaunch Chrome with remote debugging

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

This uses your normal profile (extensions, bookmarks, logins preserved). Make sure the entire command is on **one line**.

If you want a clean profile instead:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

Verify it's working:

```bash
curl http://127.0.0.1:9222/json/version
```

You should see a JSON response with browser version info.

### 3. Configure Playwright MCP to connect via CDP

In `~/.claude.json`, set the top-level `mcpServers` to include Playwright with `--cdp-endpoint`:

```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--cdp-endpoint=http://127.0.0.1:9222"
      ],
      "env": {}
    }
  }
}
```

Use `127.0.0.1` (not `localhost`) to avoid IPv6 resolution issues.

### 4. Launch ttyd

```bash
ttyd -W -p 7681 env -u CLAUDECODE bash -c claude
```

- `-W` enables write mode (allows typing input)
- `env -u CLAUDECODE` unsets the env var so Claude Code doesn't block as a "nested session"
- Runs on port 7681

### 5. Open the session

Navigate to `http://localhost:7681` in any browser. You now have a Claude Code session that controls the same Chrome instance.

Test with: `Take a screenshot of the current browser page`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ECONNREFUSED 127.0.0.1:9222` | Chrome isn't running with the debug flag. Fully quit Chrome (Cmd+Q) and relaunch with `--remote-debugging-port=9222`. |
| `Opening in existing browser session` | Regular Chrome was still running and intercepted the launch. Quit it first (Cmd+Q), then relaunch. |
| `EADDRINUSE` on port 7681 | Previous ttyd still running. Run `pkill -f ttyd`, wait a second, then relaunch. |
| `Claude Code cannot be launched inside another Claude Code session` | Use `env -u CLAUDECODE` in the ttyd command (see step 4). |
| Claude opens its own browser instead of yours | Make sure the Playwright MCP config has `--cdp-endpoint=http://127.0.0.1:9222` and does NOT have `--browser chromium` or `--user-data-dir`. Restart ttyd after config changes. |
| Missing extensions/bookmarks | You launched Chrome with `--user-data-dir`. Omit that flag to use your default profile. |
| `ECONNREFUSED ::1:9222` (IPv6) | Use `127.0.0.1` instead of `localhost` in the `--cdp-endpoint` URL. |
