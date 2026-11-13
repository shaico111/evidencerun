"""Extract a site dump, count the Stage-A frame (full population), draw the seeded sample, and
fetch full texts (Posts/Comments/PostHistory) for the sampled pool only.

usage: python -I 02_frame_and_fetch.py <site>
Writes (committed): results/funnel_<site>.csv, results/sample_manifest_<site>.csv, results/fetch_errors_<site>.csv
Writes (gitignored): raw/<site>/*.xml, raw/<site>/frame.pkl, raw/<site>/pool.pkl
"""
import pickle
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from se_common import *  # noqa
from temporal import html_to_text, BODY_TYPES  # noqa

site = sys.argv[1]
cfg = CONFIG["sites"][site]
d = RAW / site
d.mkdir(parents=True, exist_ok=True)
t0 = time.time()
log = lambda *a: print(f"[{time.time() - t0:7.0f}s]", *a, flush=True)

# ---- 1. extract needed members (streamed to disk by py7zr)
need = ["Posts.xml", "PostHistory.xml", "Comments.xml"]
if not all((d / n).exists() for n in need):
    import py7zr
    with py7zr.SevenZipFile(RAW / cfg["archive"]) as z:
        names = z.getnames()
        log("archive members:", names)
        z.extract(path=d, targets=need)
log("extracted", {n: (d / n).stat().st_size for n in need})

# ---- 2. pass 1: Posts metadata
Qs, As = {}, {}
n_posts = 0
for r in iter_rows(d / "Posts.xml"):
    n_posts += 1
    t = r.get("PostTypeId")
    if t == "1":
        body = r.get("Body", "")
        title = r.get("Title", "")
        text = title + " " + html_to_text(body)
        Qs[int(r["Id"])] = dict(created=r.get("CreationDate"), owner=iint(r.get("OwnerUserId")),
                                accepted=iint(r.get("AcceptedAnswerId")), title=title, tags=r.get("Tags", ""),
                                score=iint(r.get("Score")), nwords=len(html_to_text(body).split()),
                                trouble=bool(TROUBLE_RE.search(text)), closed=bool(r.get("ClosedDate")))
    elif t == "2":
        As[int(r["Id"])] = dict(parent=iint(r.get("ParentId")), created=r.get("CreationDate"), score=iint(r.get("Score")))
log("posts", n_posts, "questions", len(Qs), "answers", len(As))

first_ans = {}
for aid, a in As.items():
    p = a["parent"]
    if p in Qs and a["created"]:
        if p not in first_ans or a["created"] < first_ans[p]:
            first_ans[p] = a["created"]

with_acc = [q for q, v in Qs.items() if v["accepted"] is not None]
resolvable = [q for q in with_acc if Qs[q]["accepted"] in As and As[Qs[q]["accepted"]]["parent"] == q]
trouble = [q for q in resolvable if Qs[q]["trouble"]]
longenough = [q for q in trouble if Qs[q]["nwords"] >= 20]
cand = set(longenough)

# ---- 3. pass 2: light Comments + PostHistory for the candidate set (interaction-before-first-answer test)
pre_comment, pre_edit, hist_present, init_missing = set(), set(), set(), set(cand)
for r in iter_rows(d / "Comments.xml"):
    q = iint(r.get("PostId"))
    if q in cand and r.get("CreationDate") and q in first_ans and r["CreationDate"] < first_ans[q]:
        pre_comment.add(q)
log("comments pass done; threads with pre-answer comment:", len(pre_comment))
for r in iter_rows(d / "PostHistory.xml"):
    q = iint(r.get("PostId"))
    if q not in cand:
        continue
    hist_present.add(q)
    ty = iint(r.get("PostHistoryTypeId"))
    if ty == 2:
        init_missing.discard(q)
    if ty in (5, 8) and q in first_ans and r.get("CreationDate") and r["CreationDate"] < first_ans[q]:
        pre_edit.add(q)
log("history pass done; pre-answer edit threads:", len(pre_edit), "no-history threads:", len(cand - hist_present),
    "no-initial-body:", len(init_missing))
stageA = sorted(q for q in cand if q in pre_comment or q in pre_edit)
funnel = [
    ("all_posts_rows", n_posts),
    ("questions", len(Qs)),
    ("questions_with_AcceptedAnswerId", len(with_acc)),
    ("accepted_id_resolves_to_answer_of_same_question", len(resolvable)),
    ("and_troubleshooting_lexical_filter", len(trouble)),
    ("and_question_body_>=20_words", len(longenough)),
    ("  of which: no PostHistory rows at all", len(cand - hist_present)),
    ("  of which: PostHistory lacks Initial Body (type 2)", len(init_missing)),
    ("and_>=1_pre_first_answer_comment_or_body_edit  == STAGE-A FRAME", len(stageA)),
]
write_csv(RES / f"funnel_{site}.csv", [dict(site=site, step=s, count=c) for s, c in funnel])
log("STAGE-A frame", len(stageA))
pickle.dump(dict(stageA=stageA, funnel=funnel, n_with_hist=len(hist_present & cand)), open(d / "frame.pkl", "wb"))

# ---- 4. seeded sample (shuffle of the sorted frame; first K = audit sample; first M = pool)
rng = random.Random(CONFIG["random_seed"])
order = list(stageA)
rng.shuffle(order)
over = order[: CONFIG["pool_oversample_for_dedupe"]]
need_q = set(over)

# ---- 5. pass 3: full texts for oversampled threads
errors = []
QT, AT, CT, HT = {}, defaultdict(list), defaultdict(list), defaultdict(list)
for r in iter_rows(d / "Posts.xml"):
    t = r.get("PostTypeId")
    if t == "1" and int(r["Id"]) in need_q:
        QT[int(r["Id"])] = dict(final_body=r.get("Body", ""), title=r.get("Title", ""), tags=r.get("Tags", ""),
                                owner=iint(r.get("OwnerUserId")), created=r.get("CreationDate"),
                                accepted=iint(r.get("AcceptedAnswerId")), last_edit=r.get("LastEditDate"))
    elif t == "2" and iint(r.get("ParentId")) in need_q:
        AT[iint(r["ParentId"])].append(dict(id=int(r["Id"]), created=r.get("CreationDate"), body=r.get("Body", ""),
                                            owner=iint(r.get("OwnerUserId")), score=iint(r.get("Score"))))
for r in iter_rows(d / "Comments.xml"):
    q = iint(r.get("PostId"))
    if q in need_q:
        CT[q].append(dict(id=int(r["Id"]), created=r.get("CreationDate"), user=iint(r.get("UserId")),
                          text=r.get("Text", ""), score=iint(r.get("Score"))))
for i, r in enumerate(iter_rows(d / "PostHistory.xml")):
    q = iint(r.get("PostId"))
    if q in need_q and iint(r.get("PostHistoryTypeId")) in (1, 2, 5, 8):
        HT[q].append(dict(type=iint(r["PostHistoryTypeId"]), created=r.get("CreationDate"), user=iint(r.get("UserId")),
                          text=r.get("Text", ""), revision_guid=r.get("RevisionGUID"), order=i))
log("texts fetched", len(QT), len(HT))


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


# ---- 6. dedupe (exact normalised title or exact normalised accepted-answer text) and record every exclusion
seen_t, seen_a, pool, excl = set(), set(), [], []
for q in over:
    if q not in QT:
        errors.append(dict(site=site, question_id=q, error="question_row_missing_in_pass3")); continue
    acc = next((a for a in AT[q] if a["id"] == QT[q]["accepted"]), None)
    if acc is None:
        errors.append(dict(site=site, question_id=q, error="accepted_answer_row_missing_in_pass3")); continue
    kt, ka = norm(QT[q]["title"]), norm(html_to_text(acc["body"]))
    if kt in seen_t or ka in seen_a:
        excl.append(dict(site=site, question_id=q, reason="duplicate_title" if kt in seen_t else "duplicate_accepted_answer"))
        continue
    seen_t.add(kt); seen_a.add(ka)
    pool.append(q)
pool = pool[: CONFIG["pool_per_site"]]
audit = pool[: CONFIG["audit_sample_per_site"]]
base = f"https://{'askubuntu.com' if site == 'askubuntu' else 'serverfault.com'}/questions/"
man = []
for rank, q in enumerate(pool):
    man.append(dict(site=site, question_id=q, url=base + str(q), accepted_answer_id=QT[q]["accepted"],
                    sample_rank=rank, in_audit_sample=int(q in set(audit)), in_pool=1))
write_csv(RES / f"sample_manifest_{site}.csv", man)
write_csv(RES / f"fetch_errors_{site}.csv", errors + excl, ["site", "question_id", "error", "reason"])
pickle.dump(dict(pool=pool, audit=audit, QT={q: QT[q] for q in pool}, AT={q: AT[q] for q in pool},
                 CT={q: CT.get(q, []) for q in pool}, HT={q: HT.get(q, []) for q in pool},
                 excluded=excl, errors=errors, Qmeta={q: Qs[q] for q in pool}), open(d / "pool.pkl", "wb"))
log("DONE pool", len(pool), "audit", len(audit), "excluded", len(excl), "errors", len(errors))
