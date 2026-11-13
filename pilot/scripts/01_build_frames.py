"""Build full sampling frames for the three sources (no sampling yet)."""
import csv, json, re, sys, time, urllib.parse
from datetime import datetime, timezone
from common import ROOT, CONFIG, get, get_json

OUT = ROOT / "sampling_frames"


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def gitlab():
    proj = urllib.parse.quote(CONFIG["gitlab"]["project"], safe="")
    rows, page = [], 1
    while True:
        url = (f"https://gitlab.com/api/v4/projects/{proj}/issues?issue_type=incident"
               f"&state=all&order_by=created_at&sort=asc&per_page=100&page={page}")
        data = get_json(url)
        if not data:
            break
        for i in data:
            rows.append(dict(case_id=i["iid"], created_at=i["created_at"], closed_at=i.get("closed_at") or "",
                             state=i["state"], user_notes_count=i["user_notes_count"],
                             confidential=i.get("confidential", False), labels="|".join(i["labels"]),
                             title=i["title"], url=i["web_url"]))
        page += 1
        time.sleep(0.2)
    write_csv(OUT / "gitlab_frame.csv", rows, list(rows[0]))
    return len(rows)


def wikimedia():
    api = CONFIG["wikimedia"]["api"]
    titles, cont = [], {}
    while True:
        q = {"action": "query", "list": "allpages", "apprefix": "Incidents/", "apnamespace": 0,
             "apfilterredir": "nonredirects", "aplimit": 500, "format": "json", **cont}
        d = get_json(api + "?" + urllib.parse.urlencode(q))
        titles += [p["title"] for p in d["query"]["allpages"]]
        if "continue" not in d:
            break
        cont = d["continue"]
    raw_n = len(titles)
    pat = re.compile(r"^Incidents/(\d{4}-?\d{2}-?\d{2})[^/]*$")
    rows = []
    for t in titles:
        m = pat.match(t)
        if m:
            rows.append(dict(case_id=t, date=m.group(1), url="https://wikitech.wikimedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"), safe="/_-")))
    write_csv(OUT / "wikimedia_frame.csv", rows, ["case_id", "date", "url"])
    return raw_n, len(rows)


def mantis():
    base = ROOT / "raw/mantis/extracted"
    doms = set(CONFIG["mantis"]["domains"])
    rows, allcounts = [], {}
    for split in ("train", "dev", "test"):
        d = json.load(open(base / f"merged_{split}.json", encoding="utf8"))
        for k, v in d.items():
            allcounts[v["category"]] = allcounts.get(v["category"], 0) + 1
            if v["category"] in doms:
                rows.append(dict(case_id=f"{split}:{k}", split=split, domain=v["category"], title=v["title"],
                                 dialog_time=v["dialog_time"], n_utterances=len(v["utterances"])))
    write_csv(OUT / "mantis_frame.csv", rows, list(rows[0]))
    return len(rows), allcounts


if __name__ == "__main__":
    info = {"built_at_utc": datetime.now(timezone.utc).isoformat()}
    info["gitlab_frame_size"] = gitlab(); print(info)
    info["wikimedia_raw_incident_prefix_pages"], info["wikimedia_frame_size"] = wikimedia(); print(info)
    info["mantis_frame_size"], info["mantis_all_domain_counts"] = mantis(); print(info)
    (ROOT / "provenance/frame_build.json").write_text(json.dumps(info, indent=2), encoding="utf8")
