"""Record archive size, SHA-1 (vs Internet Archive manifest), SHA-256, member list and licence notes."""
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from se_common import *  # noqa

out = {"checked_on": str(date.today()), "item": "https://archive.org/details/stackexchange",
       "snapshot_note": "Internet Archive 'stackexchange' item; per-site 7z last modified 2024-04-07 (before Stack Exchange's July 2024 change of dump process). Exact dump quarter is not stated inside the archive; treat as ~2024-04 snapshot.",
       "license": {
           "content": "CC BY-SA 4.0 per the Internet Archive item description (older posts CC BY-SA 2.5/3.0 depending on date; per-post licence is not recorded in the dump rows).",
           "attribution_required": "Source link per question, author names + profile links per Q/A, as described on the item page.",
           "uncertainties": ["Stack Exchange 2024 reportedly restricted new dumps (non-commercial, no LLM training); the April-2024 IA copy predates it but its permitted use for model training/redistribution is unresolved -> HUMAN/LEGAL REVIEW REQUIRED.",
                             "No raw third-party text is committed; only IDs, URLs, statistics and short excerpts."],
           "sources_checked": ["https://archive.org/metadata/stackexchange", "https://creativecommons.org/licenses/by-sa/4.0/",
                               "https://www.devclass.com/development/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-critics-complain-this-contradicts-license/1625192",
                               "https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede"]},
       "sites": {}}
for site, c in CONFIG["sites"].items():
    p = RAW / c["archive"]
    t = time.time()
    s1 = sha1(p)
    out["sites"][site] = dict(url=c["url"], size_bytes=p.stat().st_size, expected_size=c["ia_size"],
                              sha1=s1, ia_sha1=c["ia_sha1"], sha1_matches_ia=(s1 == c["ia_sha1"]), sha256=sha256(p),
                              hash_seconds=round(time.time() - t, 1))
    d = RAW / site
    out["sites"][site]["extracted_files"] = {f.name: f.stat().st_size for f in d.glob("*.xml")} if d.exists() else {}
(PILOT / "provenance").mkdir(exist_ok=True)
json.dump(out, open(PILOT / "provenance" / "sources.json", "w"), indent=1)
print(json.dumps(out["sites"], indent=1))
