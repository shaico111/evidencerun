"""Fetch the sampled cases. Failures are kept (denominator stays 100)."""
import csv, json, time, urllib.parse
from common import ROOT, CONFIG, get, get_json

RAW = ROOT / "raw"


def rows(name):
    with open(ROOT / "samples" / name, encoding="utf8") as f:
        return list(csv.DictReader(f))


def gitlab():
    proj = urllib.parse.quote(CONFIG["gitlab"]["project"], safe="")
    status = {}
    for r in rows("gitlab_sample.csv"):
        iid = r["case_id"]
        try:
            if (RAW / "gitlab" / f"{iid}.json").exists():
                status[iid] = "ok"; continue
            issue = get_json(f"https://gitlab.com/api/v4/projects/{proj}/issues/{iid}")
            # /notes API needs auth; the public web endpoint discussions.json does not
            disc = get_json(f"https://gitlab.com/{CONFIG['gitlab']['project']}/-/issues/{iid}/discussions.json")
            notes = [dict(id=n["id"], body=n.get("note", ""), system=n.get("system", False),
                          created_at=n.get("created_at", ""), author={"username": (n.get("author") or {}).get("username", "")})
                     for dd in disc for n in dd.get("notes", [])]
            (RAW / "gitlab" / f"{iid}.json").write_text(json.dumps({"issue": issue, "notes": notes}), encoding="utf8")
            status[iid] = "ok"
        except Exception as e:
            status[iid] = f"fail:{e}"
        time.sleep(0.25)
    return status


def wikimedia():
    api = CONFIG["wikimedia"]["api"]
    status = {}
    for r in rows("wikimedia_sample.csv"):
        t = r["case_id"]
        key = t.replace("/", "_").replace(" ", "_")
        if (RAW / "wikimedia" / f"{key}.json").exists():
            status[t] = "ok"; continue
        try:
            q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content|timestamp", "rvslots": "main",
                                        "titles": t, "format": "json", "formatversion": 2})
            d = get_json(api + "?" + q)
            page = d["query"]["pages"][0]
            if page.get("missing"):
                raise RuntimeError("missing")
            rev = page["revisions"][0]
            (RAW / "wikimedia" / f"{key}.json").write_text(json.dumps({"title": t, "rev_ts": rev["timestamp"], "wikitext": rev["slots"]["main"]["content"]}), encoding="utf8")
            status[t] = "ok"
        except Exception as e:
            status[t] = f"fail:{e}"
        time.sleep(0.2)
    return status


def mantis():
    ids = {r["case_id"] for r in rows("mantis_sample.csv")}
    by_split = {}
    for i in ids:
        s, k = i.split(":", 1)
        by_split.setdefault(s, set()).add(k)
    out, status = {}, {}
    for s, keys in by_split.items():
        d = json.load(open(RAW / "mantis/extracted" / f"merged_{s}.json", encoding="utf8"))
        for k in keys:
            if k in d:
                out[f"{s}:{k}"] = d[k]
    for i in ids:
        status[i] = "ok" if i in out else "fail:not in file"
    (RAW / "mantis" / "sample.json").write_text(json.dumps(out), encoding="utf8")
    return status


if __name__ == "__main__":
    res = {"gitlab": gitlab(), "wikimedia": wikimedia(), "mantis": mantis()}
    (ROOT / "results" / "fetch_status.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    for k, v in res.items():
        print(k, sum(1 for x in v.values() if x == "ok"), "/", len(v))
