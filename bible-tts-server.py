#!/usr/bin/env python
"""
Free narrator server for bible-tts.html  (Hermes Bible)
- Serves the app page at http://127.0.0.1:8747
- /tts     -> Microsoft neural voices via edge-tts (free, unlimited, no account), MP3 cached on disk
- /api/*   -> cached proxy of bible-api.com (public-domain bible text)
- /voices  -> list of English neural voices
All data stays on your machine; caches live next to this file (bible-*-cache).

Run:  uv run --with edge-tts python "D:\\Hermes\\Projects\\e8-bible\\bible-tts-server.py"
Or:   double-click "Start Bible Audio.bat"
"""
import asyncio, hashlib, json, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

import edge_tts

ROOT      = os.path.dirname(os.path.abspath(__file__))
HTML      = os.path.join(ROOT, "bible-tts.html")
DATA_DIR  = os.path.join(ROOT, "bible-data-cache")
AUDIO_DIR = os.path.join(ROOT, "bible-audio-cache")
PORT      = 8747
API       = "https://bible-api.com/"
UA        = {"User-Agent": "hermes-bible/1.0"}

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

_voices_cache = None
_voices_lock  = threading.Lock()

# ---------------------------------------------------------------- tts
def gen_audio(text: str, voice: str, rate: str = "+0%") -> bytes:
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode("utf-8")).hexdigest()
    out = os.path.join(AUDIO_DIR, key + ".mp3")
    if not (os.path.exists(out) and os.path.getsize(out) > 0):
        async def _g():
            await edge_tts.Communicate(text, voice=voice, rate=rate).save(out)
        try:
            asyncio.run(asyncio.wait_for(_g(), timeout=45))
        except Exception as e:
            if os.path.exists(out):
                try: os.remove(out)
                except OSError: pass
            raise RuntimeError(f"tts generation failed: {e}")
    with open(out, "rb") as f:
        return f.read()

# ---------------------------------------------------------------- voices
def get_voices():
    global _voices_cache
    with _voices_lock:
        if _voices_cache is not None:
            return _voices_cache
        try:
            raw = asyncio.run(edge_tts.list_voices())
        except Exception:
            raw = []
        _voices_cache = [
            {"name": v["ShortName"], "gender": v.get("Gender", ""), "locale": v.get("Locale", "")}
            for v in raw if (v.get("Locale") or "").lower().startswith("en")
        ]
        _voices_cache.sort(key=lambda x: (not x["name"].startswith("en-US"),
                                          not x["name"].startswith("en-GB"), x["name"]))
        return _voices_cache

# ---------------------------------------------------------------- api proxy
def api_proxy(rawpath: str):
    """rawpath like '/data/web/JHN/3' or '/john+3:16?translation=web'. Cached except random."""
    url = API + rawpath.lstrip("/")
    cacheable = "/random" not in rawpath
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()
    fp  = os.path.join(DATA_DIR, key + ".json")
    if cacheable and os.path.exists(fp) and os.path.getsize(fp) > 0:
        with open(fp, "rb") as f:
            return 200, f.read()
    try:
        req = Request(url, headers=UA)
        with urlopen(req, timeout=20) as r:
            body = r.read()
            code = r.status
    except Exception as e:
        code = getattr(getattr(e, "fp", None), "status", None) or 502
        body = json.dumps({"error": str(e)[:200]}).encode()
    if cacheable and code == 200:
        tmp = fp + ".tmp"
        with open(tmp, "wb") as f:
            f.write(body)
        os.replace(tmp, fp)
    return code, body

# ---------------------------------------------------------------- handler
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, ctype, body, extra=None):
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path
        try:
            if p in ("/", "/index.html"):
                try:
                    with open(HTML, "rb") as f:
                        return self._send(200, "text/html; charset=utf-8", f.read())
                except OSError:
                    return self._send(500, "text/plain", b"bible-tts.html not found next to this server")

            if p == "/tts/ping":
                return self._send(200, "text/plain", b"pong")

            if p == "/voices":
                vs = get_voices()
                return self._send(200, "application/json", json.dumps(vs).encode())

            if p == "/tts":
                q = parse_qs(u.query)
                text  = (q.get("text") or [""])[0].strip()[:4000]
                voice = (q.get("voice") or ["en-US-GuyNeural"])[0]
                rate  = (q.get("rate") or ["1"])[0]
                try:
                    pct = int(round((float(rate) - 1.0) * 100))
                except ValueError:
                    pct = 0
                pct = max(-50, min(100, pct))
                rs = f"{'+' if pct >= 0 else '-'}{abs(pct)}%"
                if not text:
                    return self._send(400, "text/plain", b"no text")
                body = gen_audio(text, voice, rs)
                return self._send(200, "audio/mpeg", body, {"Cache-Control": "public, max-age=31536000"})

            if p.startswith("/api"):
                code, body = api_proxy(self.path[len("/api"):])
                return self._send(code, "application/json; charset=utf-8", body)

            return self._send(404, "text/plain", b"not found")
        except Exception as e:
            self._send(500, "text/plain", f"server error: {e}".encode()[:300])

if __name__ == "__main__":
    print(f"E8 Digital - Bible narrator  ->  http://127.0.0.1:{PORT}")
    print("Keep this window open while listening. Close it to stop.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
