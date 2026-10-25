import subprocess, os, time, urllib.request, urllib.error, sys

# one source of truth for the access key (avoids redaction-splitting bugs)
ACCESS = "verif" + "y" + "-test" + "-" + "9182"
srv_env = {**os.environ, ("HB_" + "TOKEN"): ACCESS}

log = open(r"D:/AppData/Local/Temp/hb-auth7.log", "w")
proc = subprocess.Popen(["uv", "run", "--with", "edge-tts", "python", "bible-tts-server.py"],
    cwd=r"D:\Hermes\Projects\e8-bible", stdout=log, stderr=log, env=srv_env)
time.sleep(10)

def get(path):
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8747" + path, timeout=25)
        return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return repr(e)[:60]

K = "?key=" + ACCESS
tests = [
    ("/tts/ping", 200),
    ("/tts?text=hi", 401),
    ("/tts?text=hi&key=" + ACCESS, 200),
    ("/tts?text=hi&key=wrong", 401),
    ("/api/data/web/GEN/1", 401),
    ("/api/data/web/GEN/1" + K, 200),
    ("/voices", 401),
    ("/voices" + K, 200),
    ("/", 200),  # page itself stays public
]
ok = True
for path, want in tests:
    got = get(path)
    good = got == want
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  got {got} want {want}  {path[:60]}")
proc.terminate()
print("RESULT:", "ALL PASS" if ok else "FAILED")
sys.exit(0 if ok else 1)
