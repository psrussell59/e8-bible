# E8 Digital - Bible

Free Bible reader + neural narrator. No accounts, no keys, no cost.

## Files
- `bible-tts.html` — the app (reader, TTS player, 10 public-domain translations)
- `bible-tts-server.py` — local narrator server (edge-tts voices + bible-api proxy/cache), port 8747
- `Start Bible Audio.bat` — one-double-click launcher (starts server, opens browser)
- `bible-audio-cache/` — generated narration MP3s, cached forever by voice+speed+text
- `bible-data-cache/` — cached bible-api.com JSON (bypasses the 15 req/30s rate limit)

## Run
- **Windows:** double-click **Start Bible Audio.bat**, then use `http://127.0.0.1:8747` in Edge/Chrome.
- **macOS / Linux:** run **start-bible-audio.command** (double-click on Mac; first time may need
  `chmod +x` or right-click → Open). Then open `http://127.0.0.1:8747` in Safari/Chrome.
- Without the server, open `bible-tts.html` directly — it falls back to browser voices
  (Safari's voices are decent but the neural narrator needs the server).

Requires: `uv` (https://docs.astral.sh/uv/) — edge-tts installs itself on first run.

## Notes
- YLT translation is New Testament only (OT books 404 there, by design).
- Speed slider: 0.50–2.00× in 0.05 steps (baked into MP3s). Gap slider: 0–3s verse pause.
- Settings & last passage persist in browser localStorage; URL hashes deep-link passages (`#kjv/John 3:16`).
