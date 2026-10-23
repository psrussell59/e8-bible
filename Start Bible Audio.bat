@echo off
rem Starts the free neural narrator for Hermes Bible, then opens the app in your browser.
title E8 Digital - Bible
echo Starting narrator server (free Microsoft neural voices via edge-tts)...
start "" /min cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8747"
uv run --with edge-tts python "%~dp0bible-tts-server.py"
