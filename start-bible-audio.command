#!/bin/bash
# E8 Digital - Bible narrator launcher (macOS) — double-click to start.
# Starts the free neural narrator server (edge-tts) and opens the app in your browser.
cd "$(dirname "$0")" || exit 1

( sleep 3; open http://127.0.0.1:8747 ) &

if command -v uv >/dev/null 2>&1; then
    echo "E8 Digital - Bible narrator (uv + edge-tts)"
    exec uv run --with edge-tts python bible-tts-server.py
elif command -v python3 >/dev/null 2>&1; then
    echo "uv not found; trying pip3 install edge-tts..."
    if python3 -m pip install --user edge-tts 2>/dev/null || python3 -m pip install --break-system-packages edge-tts 2>/dev/null; then
        exec python3 bible-tts-server.py
    else
        echo "edge-tts install failed. Install uv instead:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
else
    echo "python3 not found. Install the Xcode command line tools first:"
    echo "  xcode-select --install"
    echo "then install uv:  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
