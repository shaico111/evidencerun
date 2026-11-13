"""Shared helpers for the Stack Exchange raw-validation pilot (stdlib only, plus reuse of the
earlier pilot's Wilson-interval helper so the statistics are identical across both pilots)."""
import csv
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1]
REPO = PILOT.parents[1]
RAW = PILOT / "raw"
RES = PILOT / "results"
CONFIG = json.loads((PILOT / "config.json").read_text(encoding="utf8"))


def wilson(k, n, z=1.96):  # same formula as pilot/scripts/common.py (kept local: that module reads a different config at import)
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def fmt_ci(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100 * k / n:.1f}% (95% CI {100 * lo:.1f}-{100 * hi:.1f}%)" if n else f"{k}/0"


def iter_rows(path):
    """Stream <row> attribute dicts from a Stack Exchange dump XML file."""
    for _, el in ET.iterparse(str(path), events=("end",)):
        if el.tag == "row":
            yield el.attrib
            el.clear()


def sha256(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha1(path, chunk=1 << 24):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def write_csv(path, rows, fields=None):
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else [])
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def iint(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


TROUBLE_RE = re.compile(
    r"(error|fail|not work|n't work|doesn.t|won.t|can.t|cannot|unable|crash|broken|issue|problem|stuck|"
    r"freez|hang|no longer|denied|time.?out|refused|missing|not found|unexpected|why (?:does|is|do|am)|slow|"
    r"warning|exception|segfault|panic|boot|not (?:start|load|show|detect|recogni|connect|mount))", re.I)
