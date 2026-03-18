#!/bin/bash

# Kill any existing ttyd and Chrome
pkill -f ttyd 2>/dev/null || true
pkill -9 -f "Google Chrome" 2>/dev/null || true

# Wait for Chrome to fully die
echo "Waiting for Chrome to quit..."
for i in {1..10}; do
  pgrep -f "Google Chrome" > /dev/null 2>&1 || break
  sleep 1
done

# Wipe the temp profile so Chrome never restores old sessions/windows
rm -rf /tmp/chrome-debug

# Start ttyd FIRST so localhost:7681 is ready before Chrome loads it
echo "Starting ttyd..."
ttyd -W -p 7681 env -u CLAUDECODE bash -c claude &

# Wait for ttyd to be ready
echo "Waiting for ttyd..."
for i in {1..15}; do
  curl -sf http://127.0.0.1:7681 > /dev/null 2>&1 && break
  sleep 1
done

# Launch Chrome with remote debugging, opening localhost:7681 as the only tab
echo "Launching Chrome..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug \
  --no-first-run \
  --disable-session-crashed-bubble \
  "http://localhost:7681" &

echo ""
echo "========================================"
echo "  Chrome is opening Claude Code at:"
echo "  http://localhost:7681"
echo "========================================"
wait
