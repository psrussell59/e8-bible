# E8 Digital - Bible

Free Bible reader + neural narrator. No accounts, no keys, no cost.

## Files
- `bible-tts.html` — the app (reader, TTS player, 10 public-domain translations)
- `bible-tts-server.py` — local narrator server (edge-tts voices + bible-api proxy/cache), port 8747
- `Start Bible Audio.bat` — one-double-click launcher (starts server, opens browser)
- `bible-audio-cache/` — generated narration MP3s, cached forever by voice+speed+text
- `bible-data-cache/` — cached bible-api.com JSON (bypasses the 15 req/30s rate limit)

## Run
- **Hosted (recommended):** open **https://bible.e8digitalmedia.com** — the server injects its
  access key into the page automatically; neural voices and text proxy work with zero setup.
  To use local instead on a device: ⚙ → Base URL `http://127.0.0.1:8747`, key blank → Save.
- **Windows local:** double-click **Start Bible Audio.bat**, then use `http://127.0.0.1:8747` in Edge/Chrome.
- **macOS / Linux:** run **start-bible-audio.command** (double-click on Mac; first time may need
  `chmod +x` or right-click → Open). Then open `http://127.0.0.1:8747` in Safari/Chrome.
- Without the server, open `bible-tts.html` directly — it falls back to browser voices
  (Safari's voices are decent but the neural narrator needs the server).

Requires: `uv` (https://docs.astral.sh/uv/) — edge-tts installs itself on first run.

## Remote / hosted deployment
To run the narrator on a server (e.g. an EC2 box) instead of your PC:
1. `git clone` this repo there, then run the server with one env var:
   `HB_TOKEN=*** your secret>` (required — gates `/tts`, `/api`, `/voices`).
   It binds `127.0.0.1:8747` by default, which is what you want behind a same-box proxy.
2. Put Caddy/nginx in front for HTTPS + TLS, proxying to `127.0.0.1:8747` (same box).
   Keep the default local bind — only set `HB_BIND=0.0.0.0` if the proxy runs on a
   different machine, and firewall 8747 in that case.
3. In the app, click **⚙** (top right) → enter the server's `https://…` URL and the
   same access key → Save. `/tts/ping` and the page itself stay open; everything else 401s without the key.
4. To go back to the local launcher, ⚙ → Reset local.

`uv run python test-auth.py` (needs a free 8747) checks the whole auth matrix.

## Notes
- YLT translation is New Testament only (OT books 404 there, by design).
- Speed slider: 0.50–2.00× in 0.05 steps (baked into MP3s). Gap slider: 0–3s verse pause.
- Settings & last passage persist in browser localStorage; URL hashes deep-link passages (`#kjv/John 3:16`).
