import json, math, time, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf8"))
UA = "evidencerun-feasibility-pilot/0.1 (course research; polite rate)"


def get(url, retries=6, timeout=60, want_headers=False):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                return (body, dict(r.headers), r.status) if want_headers else body
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (404, 403, 410, 401):
                raise
            time.sleep(15 * (i + 1) if e.code == 429 else 2 ** i)
        except Exception as e:  # network hiccup
            last = e
            time.sleep(2 ** i)
    raise last


def get_json(url, **kw):
    return json.loads(get(url, **kw).decode("utf8"))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
