"""Automated PROXY analysis of the sampled cases.

This is NOT the human annotation required by the protocol. It computes objective, reproducible
proxies (fetchability, timestamped-contribution counts, explicit link presence, link
accessibility). Proxies are meant to be upper bounds for the protocol's viability criteria
where possible; relationship_grade and 'material new fact' still need human adjudication.
"""
import csv, json, re, time, urllib.parse
from collections import Counter
from common import ROOT, CONFIG, get, get_json, wilson

RAW = ROOT / "raw"
status = json.loads((ROOT / "results/fetch_status.json").read_text(encoding="utf8"))
LINK_CACHE = {}


def link_ok(url, min_chars=300):
    """Return (accessible, nchars). Accessible = HTTP 200 and enough visible text."""
    if url in LINK_CACHE:
        return LINK_CACHE[url]
    try:
        b = get(url, retries=2, timeout=25)
        txt = re.sub(r"<[^>]+>", " ", b.decode("utf8", "ignore"))
        res = (len(txt) >= min_chars, len(txt))
    except Exception:
        res = (False, 0)
    LINK_CACHE[url] = res
    return res


SUBSTANTIVE = 80  # chars for a contribution to count as potentially adding a fact

# ---------------- GitLab ----------------
RB = re.compile(r"https?://(?:runbooks\.gitlab\.com|gitlab\.com/gitlab-com/runbooks)[^\s)>\]\"'`]*")


def gitlab():
    out = []
    for iid, st in status["gitlab"].items():
        rec = dict(source="gitlab", case_id=iid, fetched=st == "ok")
        if not rec["fetched"]:
            rec["fail"] = st
            out.append(rec)
            continue
        d = json.loads((RAW / "gitlab" / f"{iid}.json").read_text(encoding="utf8"))
        issue, notes = d["issue"], d["notes"]
        human = [n for n in notes if not n["system"] and "bot" not in n["author"]["username"].lower()
                 and len(n["body"]) >= SUBSTANTIVE]
        body = issue.get("description") or ""
        rec["n_human_notes"] = len(human)
        rec["desc_len"] = len(body)
        title = issue["title"].lower()
        rec["case_valid_proxy"] = bool((len(body) >= 300 or human) and not issue.get("confidential")
                                       and not re.search(r"maintenance|\bchange request\b|\btest\b", title))
        rec["stage3_proxy"] = rec["case_valid_proxy"] and len(human) >= 2 and len(body) >= 100
        rec["chronology_grade_proxy"] = 2 if rec["stage3_proxy"] else 0
        texts = [("description", issue["created_at"], body)] + [
            (f"note{n['id']}", n["created_at"], n["body"]) for n in notes if not n["system"]]
        links = {}
        for src, ts, t in texts:
            for u in RB.findall(t):
                u = u.rstrip(".,;")
                links.setdefault(u.split("#")[0], ts)
        rec["runbook_links"] = sorted(links)
        closed = issue.get("closed_at")
        rec["retro_link_only"] = bool(links) and bool(closed) and all(ts > closed for ts in links.values())
        acc = {u: link_ok(u) for u in links}
        rec["accessible_runbook_links"] = sorted(u for u, (ok, _) in acc.items() if ok)
        rec["target_proxy"] = bool(rec["accessible_runbook_links"])
        rec["tier_a_proxy"] = rec["stage3_proxy"] and rec["target_proxy"]
        rec["tier_b_proxy"] = rec["tier_a_proxy"]  # incidents have no independent accepted-answer notion
        rec["case_url"] = issue["web_url"]
        out.append(rec)
    return out


# ---------------- Wikimedia ----------------
KW = re.compile(r"runbook|troubleshoot|debug|operations|procedure|alert|failover|restart|recover|how.?to|emergency|depool|switch|maintenance|upgrade|admin|reimage|restore|cleanup", re.I)
SKIP = re.compile(r"^(Incidents?/|Incident response|Category:|File:|User|Talk:|Help:|Template:|Special:|Phab|Phabricator|Gerrit|Main Page|Deployments|Server Admin Log)", re.I)
WL = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
EXT = re.compile(r"https?://wikitech\.wikimedia\.org/wiki/([^\s\]|)<>\"']+)")
TIME = re.compile(r"(?:^|[\s*'])(\d{1,2}:\d{2})(?:\s?UTC)?", re.M)


def wikimedia():
    out, tcache, pending = [], {}, []
    for t, st in status["wikimedia"].items():
        rec = dict(source="wikimedia", case_id=t, fetched=st == "ok")
        if not rec["fetched"]:
            rec["fail"] = st
            out.append(rec)
            continue
        d = json.loads((RAW / "wikimedia" / f"{t.replace('/', '_').replace(' ', '_')}.json").read_text(encoding="utf8"))
        w = d["wikitext"]
        m = re.search(r"==+\s*Timeline\s*==+(.*?)(?=\n==[^=]|\Z)", w, re.S | re.I)
        tl = m.group(1) if m else ""
        entries = [l for l in tl.splitlines() if l.strip().startswith(("*", "|")) and TIME.search(l)]
        rec["timeline_entries"] = len(entries)
        rec["wikitext_len"] = len(w)
        rec["case_valid_proxy"] = (len(w) > 800 and "Summary" in w) or len(w) > 2500
        rec["stage3_proxy"] = rec["case_valid_proxy"] and len(entries) >= 3
        rec["chronology_grade_proxy"] = 1 if rec["stage3_proxy"] else 0  # retrospective, dated entries
        cands = set()
        for x in WL.findall(w):
            x = x.strip().replace("_", " ")
            if not SKIP.match(x) and KW.search(x):
                cands.add(x)
        for x in EXT.findall(w):
            x = urllib.parse.unquote(x).split("#")[0].replace("_", " ")
            if not SKIP.match(x) and KW.search(x):
                cands.add(x)
        rec["candidate_targets"] = sorted(cands)
        rec["no_runbook_mention"] = bool(re.search(
            r"no runbook|runbook (?:did not|didn.t|does not|doesn.t) exist|without a runbook|lack of (?:a )?runbook", w, re.I))
        rec["case_url"] = "https://wikitech.wikimedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"), safe="/_-")
        pending.append(rec)
        out.append(rec)
    allt = sorted({x for r in pending for x in r["candidate_targets"]})
    api = CONFIG["wikimedia"]["api"]
    for i in range(0, len(allt), 40):
        batch = allt[i:i + 40]
        q = urllib.parse.urlencode({"action": "query", "prop": "info|revisions", "rvprop": "size", "titles": "|".join(batch),
                                    "redirects": 1, "format": "json", "formatversion": 2})
        d = get_json(api + "?" + q)
        norm = {n["from"]: n["to"] for n in d["query"].get("normalized", [])}
        red = {n["from"]: n["to"] for n in d["query"].get("redirects", [])}
        pg = {p["title"]: p for p in d["query"]["pages"]}
        for b in batch:
            tt = norm.get(b, b)
            tt = red.get(tt, tt)
            p = pg.get(tt)
            tcache[b] = bool(p and not p.get("missing") and p.get("revisions", [{}])[0].get("size", 0) >= 800)
        time.sleep(0.3)
    for r in pending:
        r["accessible_targets"] = [x for x in r["candidate_targets"] if tcache.get(x)]
        r["target_proxy"] = bool(r["accessible_targets"])
        r["tier_a_proxy"] = r["stage3_proxy"] and r["target_proxy"]
        r["tier_b_proxy"] = r["tier_a_proxy"]
    return out


# ---------------- MANtIS ----------------
PROB = re.compile(r"error|not working|doesn.?t work|won.?t|fail|crash|can.?t|cannot|issue|problem|stuck|broken|slow|no longer|stopped|unable|freez|hang|corrupt|bug|wrong|missing", re.I)
URL = re.compile(r"href=\"(https?://[^\"]+)\"|(https?://[^\s<>\"]+)")
SE = re.compile(r"(stackexchange|stackoverflow|askubuntu|superuser|serverfault|stack\.imgur|imgur\.com|i\.stack|gravatar|sstatic)", re.I)


def mantis():
    data = json.loads((RAW / "mantis/sample.json").read_text(encoding="utf8"))
    out = []
    meta = {r["case_id"]: r for r in csv.DictReader(open(ROOT / "samples/mantis_sample.csv", encoding="utf8"))}
    for cid, st in status["mantis"].items():
        rec = dict(source="mantis", case_id=cid, fetched=st == "ok", domain=meta[cid]["domain"])
        if not rec["fetched"]:
            rec["fail"] = st
            out.append(rec)
            continue
        d = data[cid]
        u = sorted(d["utterances"], key=lambda x: x["utterance_pos"])
        seeker = [x for x in u if x["actor_type"] == "user"]
        agent = [x for x in u if x["actor_type"] == "agent"]
        ans = [x for x in agent if x.get("is_answer")]
        rec["n_seeker_turns"] = len(seeker)
        rec["n_seeker_substantive"] = sum(1 for x in seeker if len(x["utterance"]) >= 60)
        rec["case_valid_proxy"] = bool(PROB.search(seeker[0]["utterance"]) or PROB.search(d["title"]))
        rec["stage3_proxy"] = rec["case_valid_proxy"] and rec["n_seeker_substantive"] >= 3
        rec["chronology_grade_proxy"] = 2 if rec["stage3_proxy"] else 0
        # DEVIATION (recorded): this MANtIS release has is_answer == '0' for every utterance, so no
        # accepted-answer labels exist. Substitute: the top-voted answer POST (not comment) with votes >= 1.
        def votes(x):
            try:
                return int(x.get("votes") or 0)
            except Exception:
                return 0
        posts = [x for x in agent if "_" not in str(x.get("id", ""))]
        best = max(posts, key=votes, default=None)
        rec["accepted_label_present"] = bool(ans)
        rec["has_accepted_answer"] = bool(ans) or bool(best and votes(best) >= 1)
        rec["accepted_answer_len"] = len((ans or ([best] if best else []))[0]["utterance"]) if (ans or best) else 0
        urls = set()
        for x in agent:
            for a, b in URL.findall(x["utterance"]):
                uu = (a or b).rstrip(".,;)")
                if not SE.search(uu):
                    urls.add(uu.split("#")[0])
        rec["external_urls"] = sorted(urls)[:5]
        rec["accessible_external_urls"] = [x for x in rec["external_urls"] if link_ok(x, 1500)[0]]
        rec["tier_b_proxy"] = rec["stage3_proxy"] and rec["has_accepted_answer"] and rec["accepted_answer_len"] >= 100
        rec["tier_a_proxy"] = rec["stage3_proxy"] and bool(rec["accessible_external_urls"])  # relevance/type unverified
        rec["target_proxy"] = rec["tier_b_proxy"]
        out.append(rec)
    return out


def metrics(all_rows):
    rows = []
    for s in ("gitlab", "wikimedia", "mantis"):
        R = [r for r in all_rows if r["source"] == s]
        n = len(R)

        def c(f):
            return sum(1 for r in R if f(r))

        defs = [
            ("fetch_success", c(lambda r: r["fetched"])),
            ("case_valid_proxy", c(lambda r: r.get("case_valid_proxy"))),
            ("stage3_proxy_grade>=1", c(lambda r: r.get("stage3_proxy"))),
            ("stage3_observed_grade2", c(lambda r: r.get("stage3_proxy") and r.get("chronology_grade_proxy") == 2)),
            ("explicit_target_proxy", c(lambda r: r.get("target_proxy"))),
            ("tier_a_proxy_upper_bound", c(lambda r: r.get("tier_a_proxy"))),
            ("tier_b_proxy_upper_bound", c(lambda r: r.get("tier_b_proxy"))),
        ]
        for name, k in defs:
            lo, hi = wilson(k, n)
            rows.append(dict(source=s, metric=name, numerator=k, denominator=n, pct=round(100 * k / n, 1),
                             ci95_lo=round(100 * lo, 1), ci95_hi=round(100 * hi, 1)))
        tgt = Counter()
        for r in R:
            if r.get("tier_a_proxy"):
                for t in (r.get("accessible_runbook_links") or r.get("accessible_targets") or r.get("accessible_external_urls") or []):
                    tgt[t] += 1
        rows.append(dict(source=s, metric="unique_tier_a_proxy_targets", numerator=len(tgt), denominator="", pct="", ci95_lo="", ci95_hi=""))
        top10, tot = sum(v for _, v in tgt.most_common(10)), sum(tgt.values())
        rows.append(dict(source=s, metric="top10_target_share_of_pairs", numerator=top10, denominator=tot,
                         pct=round(100 * top10 / tot, 1) if tot else "", ci95_lo="", ci95_hi=""))
    return rows


if __name__ == "__main__":
    allr = gitlab() + wikimedia() + mantis()
    with open(ROOT / "annotations/auto_proxy_cases.jsonl", "w", encoding="utf8") as f:
        for r in allr:
            f.write(json.dumps(r) + "\n")
    m = metrics(allr)
    with open(ROOT / "results/metrics.csv", "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(m[0]))
        w.writeheader()
        w.writerows(m)
    for r in m:
        print(r)
