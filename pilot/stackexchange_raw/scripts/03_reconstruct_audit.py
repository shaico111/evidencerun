"""Run temporal reconstruction over the sampled pool; emit audit tables, statistics and the review queue.
usage: python -I 03_reconstruct_audit.py   (after 02_frame_and_fetch.py for each site)
"""
import json
import pickle
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from se_common import *  # noqa
from temporal import build_thread_states, html_to_text, parse_ts, tokens  # noqa

SELF_BAD = re.compile(r"(see|as (?:said|mentioned|noted|stated)|per|in|check) (?:my |the )?(?:above |previous )?comment|see above|"
                      r"as (?:above|in the question)|same as (?:above|the question)|what (?:he|she|they) (?:said|wrote)", re.I)
URL_RE = re.compile(r"https?://\S+")


def answer_quality(body_html):
    txt = html_to_text(body_html)
    no_url = URL_RE.sub("", txt)
    words = len(no_url.split())
    has_code = "<code>" in body_html or "<pre" in body_html
    link_only = len(URL_RE.findall(txt)) > 0 and words < 15
    bad = bool(SELF_BAD.search(txt))
    sc = words >= 25 and not bad and not link_only
    return dict(words=words, has_code=int(has_code), link_only=int(link_only), refers_to_comment=int(bad), self_contained_auto=int(sc))


def ts_diff_h(a, b):
    ta, tb = parse_ts(a), parse_ts(b)
    return None if ta is None or tb is None else round((ta - tb).total_seconds() / 3600, 3)


all_rows, tl_rows, aq_rows, queue, stats = [], [], [], [], {}
for site in CONFIG["sites"]:
    P = pickle.load(open(RAW / site / "pool.pkl", "rb"))
    F = pickle.load(open(RAW / site / "frame.pkl", "rb"))
    res = {}
    for q in P["pool"]:
        qt = P["QT"][q]
        meta = dict(id=q, owner=qt["owner"], created=qt["created"], title=qt["title"])
        r = build_thread_states(meta, P["HT"][q], P["CT"][q], P["AT"][q], qt["accepted"])
        acc = next((a for a in P["AT"][q] if a["id"] == qt["accepted"]), None)
        aq = answer_quality(acc["body"]) if acc else {}
        first_ans = min((a["created"] for a in P["AT"][q] if a["created"]), default=None)
        init = next((h for h in P["HT"][q] if h["type"] == 2), None)
        retro = None
        if init:
            retro = int(len(set(tokens(html_to_text(qt["final_body"]))) - set(tokens(html_to_text(init["text"])))) >= 5)  # PostHistory text is Markdown, Posts.Body is HTML: compare token content, not strings
        rej = Counter(re.sub(r"\(.*\)", "", why) for _, why in r["rejected"])
        row = dict(site=site, question_id=q, url=f"https://{'askubuntu.com' if site == 'askubuntu' else 'serverfault.com'}/questions/{q}",
                   in_audit_sample=int(q in set(P["audit"])), accepted_answer_id=qt["accepted"],
                   first_answer_at=first_ans, accepted_answer_at=acc["created"] if acc else None,
                   accepted_is_first=int(bool(acc) and acc["created"] == first_ans),
                   hours_question_to_first_answer=ts_diff_h(first_ans, qt["created"]),
                   cutoff=r["cutoff"].isoformat() if r["cutoff"] else None, cutoff_reason=r["cutoff_reason"],
                   auto_states=r["n_states"], n_accepted_units=len(r["units"]),
                   reasons="|".join(r["reasons"]), rejected_summary=";".join(f"{k}:{v}" for k, v in rej.items()),
                   leakage_auto=r["leakage"], leakage_detail=r["leakage_detail"].strip(),
                   final_body_differs_from_initial=retro, n_owner_comments_pre_cutoff=sum(1 for u in r["units"] if u["kind"] == "comment"),
                   n_body_edits_pre_cutoff=sum(1 for u in r["units"] if u["kind"] == "edit"),
                   self_answered_by_asker=int(bool(acc) and acc.get("owner") is not None and acc.get("owner") == qt["owner"]),
                   review_provenance="automated")
        res[q] = dict(row=row, r=r, aq=aq, acc=acc)
        tl_rows.append(row)
        if acc:
            aq_rows.append(dict(site=site, question_id=q, accepted_answer_id=acc["id"], accepted_score=acc["score"],
                                n_answers=len(P["AT"][q]), **aq, review_provenance="automated (relevance NOT assessed)"))
    pickle.dump({q: dict(row=v["row"], early=v["r"]["early_text"], later=v["r"]["later_text"], advanced=v["r"]["advanced_text"],
                         acc_body=v["acc"]["body"] if v["acc"] else None, units=v["r"]["units"], aq=v["aq"]) for q, v in res.items()},
                open(RAW / site / "states.pkl", "wb"))

    def tally(qs):
        n = len(qs)
        g = lambda f: sum(1 for q in qs if f(res[q]))
        two = lambda v: v["row"]["auto_states"] >= 2
        three = lambda v: v["row"]["auto_states"] >= 3
        sc = lambda v: v["aq"].get("self_contained_auto", 0) == 1
        lf = lambda v: v["row"]["leakage_auto"] == "none"
        tg = {res[q]["acc"]["id"] for q in qs if two(res[q]) and sc(res[q]) and lf(res[q]) and res[q]["acc"]}
        return dict(n=n, accepted_found=g(lambda v: v["acc"] is not None), has_initial_history=g(lambda v: "no_initial_body_in_history" not in v["row"]["reasons"]),
                    two_plus=g(two), three_plus=g(three), self_contained_auto=g(sc),
                    two_plus_selfcontained_leakfree=g(lambda v: two(v) and sc(v) and lf(v)),
                    three_plus_selfcontained_leakfree=g(lambda v: three(v) and sc(v) and lf(v)),
                    leakage_suspected=g(lambda v: not lf(v)), distinct_target_answers=len(tg),
                    self_answered=g(lambda v: v["row"]["self_answered_by_asker"] == 1),
                    accepted_is_first=g(lambda v: v["row"]["accepted_is_first"] == 1),
                    final_differs=g(lambda v: v["row"]["final_body_differs_from_initial"] == 1),
                    cutoff_by_comment=g(lambda v: v["row"]["cutoff_reason"] == "comment_discloses_solution"))
    audit_q = P["audit"]
    pool_q = P["pool"]
    stats[site] = dict(frame_size=len(F["stageA"]), funnel=F["funnel"], audit=tally(audit_q), pool=tally(pool_q))

    # stratified inspection queue from pool \ audit
    rest = [q for q in pool_q if q not in set(audit_q)]
    pos = [q for q in rest if res[q]["row"]["auto_states"] >= 2 and res[q]["row"]["leakage_auto"] == "none"]
    unc = [q for q in rest if res[q]["row"]["auto_states"] == 1 and (res[q]["row"]["rejected_summary"] and re.search(
        r"too_few_new_tokens|resolution_claim|solution_overlap|equal_timestamp|edit_by_non_owner", res[q]["row"]["rejected_summary"]))]
    neg = [q for q in rest if res[q]["row"]["auto_states"] == 1 and q not in set(unc)]
    rng = random.Random(CONFIG["random_seed"] + 1)
    qcfg = CONFIG["stratified_queue_per_site"]
    strata = {}
    for name, lst in (("auto_positive", pos), ("uncertain", unc), ("auto_negative", neg)):
        lst = list(lst); rng.shuffle(lst)
        strata[name] = lst[: qcfg[name]]
        stats[site].setdefault("strata_available", {})[name] = len(lst)
        stats[site].setdefault("strata_taken", {})[name] = len(strata[name])
    for q in audit_q:
        queue.append((site, q, "simple_random_audit"))
    for name, lst in strata.items():
        for q in lst:
            queue.append((site, q, "stratified_" + name))
    for q in pool_q:
        all_rows.append(res[q]["row"])
    globals().setdefault("RES_ALL", {})[site] = res

RES.mkdir(exist_ok=True, parents=True)
write_csv(RES / "timeline_audit.csv", tl_rows)
write_csv(RES / "accepted_answer_quality.csv", aq_rows)
json.dump(stats, open(RES / "stats.json", "w", indent=1) if False else open(RES / "stats.json", "w"), indent=1)

# human-review queue (blank human columns; automated fields prefilled)
HUM = ["troubleshooting", "accepted_answer_present", "accepted_answer_relevant", "solution_self_contained",
       "preanswer_new_fact_count", "valid_information_states", "stage_evidence", "observability", "leakage",
       "ambiguity_multiple_answers", "eligibility_verdict", "review_provenance", "reviewer", "notes"]
qrows = []
for site, q, stratum in queue:
    v = RES_ALL[site][q]
    r = v["row"]
    qrows.append(dict(site=site, question_id=q, url=r["url"], stratum=stratum, accepted_answer_id=r["accepted_answer_id"],
                      auto_states=r["auto_states"], auto_leakage=r["leakage_auto"], auto_cutoff=r["cutoff"],
                      auto_self_contained=v["aq"].get("self_contained_auto"), **{k: "" for k in HUM}))
ann = PILOT / "annotations"
ann.mkdir(exist_ok=True)
write_csv(ann / "human_review_queue.csv", qrows)
pickle.dump(queue, open(RAW / "queue.pkl", "wb"))
print(json.dumps({s: {k: v for k, v in st.items() if k != "funnel"} for s, st in stats.items()}, indent=1))
