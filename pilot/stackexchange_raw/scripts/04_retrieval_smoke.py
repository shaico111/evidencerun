"""Frozen candidate corpus + BM25 / pretrained MiniLM smoke test on automated (provisional) early/later queries.
All numbers are PRELIMINARY: relevance of accepted answers is not human-verified; eligibility is automated.
"""
import hashlib
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from se_common import *  # noqa
from temporal import html_to_text, tokens  # noqa
import numpy as np
from rank_bm25 import BM25Okapi

t0 = time.time()
docs, queries = [], []
for site in CONFIG["sites"]:
    P = pickle.load(open(RAW / site / "pool.pkl", "rb"))
    S = pickle.load(open(RAW / site / "states.pkl", "rb"))
    for q in P["pool"]:
        qt = P["QT"][q]
        for a in P["AT"][q]:
            txt = html_to_text(a["body"])
            if len(txt.split()) < 3:
                continue
            docs.append(dict(doc_id=f"{site}:a{a['id']}", site=site, thread=q, answer_id=a["id"],
                             accepted=int(a["id"] == qt["accepted"]), words=len(txt.split()), text=txt))
        s = S[q]
        r = s["row"]
        if r["auto_states"] >= 2 and r["leakage_auto"] == "none" and s["aq"].get("self_contained_auto") == 1:
            queries.append(dict(site=site, thread=q, target=f"{site}:a{qt['accepted']}", early=s["early"], later=s["later"]))
print("corpus", len(docs), "accepted", sum(d["accepted"] for d in docs), "queries", len(queries), flush=True)

# ---- near-duplicate families among accepted answers (TF-IDF cosine >= 0.9) -> frozen split by family BEFORE any use
from sklearn.feature_extraction.text import TfidfVectorizer
acc = [d for d in docs if d["accepted"]]
X = TfidfVectorizer(min_df=1, sublinear_tf=True).fit_transform([d["text"] for d in acc])
parent = list(range(len(acc)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
pairs = []
for i0 in range(0, len(acc), 500):
    sim = (X[i0:i0 + 500] @ X.T).toarray()
    for ii in range(sim.shape[0]):
        i = i0 + ii
        for j in np.where(sim[ii] >= 0.9)[0]:
            if j > i:
                pairs.append((i, int(j), float(sim[ii, j]))); parent[find(i)] = find(int(j))
fam = {acc[i]["doc_id"]: find(i) for i in range(len(acc))}
def split_of(famid):
    return "test" if int(hashlib.sha256(f"{CONFIG['random_seed']}:{famid}".encode()).hexdigest(), 16) % 10 < 3 else "train"
for d in acc:
    d["family"] = fam[d["doc_id"]]; d["split"] = split_of(d["family"])
fam_split = {d["doc_id"]: d["split"] for d in acc}
write_csv(RES / "candidate_corpus_manifest.csv",
          [dict(doc_id=d["doc_id"], site=d["site"], thread=d["thread"], answer_id=d["answer_id"],
                role="accepted_target" if d["accepted"] else "unjudged_other_answer", words=d["words"],
                family=d.get("family", ""), split=d.get("split", "")) for d in docs])
test_q = [q for q in queries if fam_split.get(q["target"]) == "test"]
fam_sizes = {}
for d in acc: fam_sizes[d["family"]] = fam_sizes.get(d["family"], 0) + 1
n_dupfam = sum(1 for v in fam_sizes.values() if v > 1)
(RES / "split_leakage_audit.md").write_text(f"""# Split / near-duplicate leakage audit (automated)

* Candidate corpus: {len(docs)} answer documents ({len(acc)} accepted targets, one per sampled thread; remaining are other answers of the same threads, labelled `unjudged`).
* Near-duplicate families among accepted answers: TF-IDF cosine >= 0.9 -> {len(pairs)} pairs, {n_dupfam} families with >1 member, largest family size {max(fam_sizes.values())}.
* Split frozen **by answer family** with a hash of (seed 42, family id) before any query/metric computation: {sum(1 for d in acc if d['split']=='test')} test / {sum(1 for d in acc if d['split']=='train')} train accepted targets (30% test target).
* All eligible queries ({len(queries)}) are evaluated for the smoke test (no training here), and the test-split subset ({len(test_q)}) is reported separately. This is the *held-out solution family* split (harder than held-out question). Held-out-question-only was not separately run.
* Not audited: near-duplicate *questions* across families (only exact normalised-title / accepted-answer duplicates were removed at sampling; see fetch_errors_*.csv), paraphrased duplicates, and cross-site duplicates. Human review pending.
* Training contamination: **no training was run**; therefore no train/test contamination can have occurred in this pilot, and this audit only prepares the split.
""", encoding="utf8")

# ---- retrieval over the same corpus for every query / method
doc_ids = [d["doc_id"] for d in docs]
idx = {d: i for i, d in enumerate(doc_ids)}
thread_docs = {}
for d in docs: thread_docs.setdefault((d["site"], d["thread"]), set()).add(idx[d["doc_id"]])
bm = BM25Okapi([tokens(d["text"]) for d in docs])
def bm25_scores(q): return np.array(bm.get_scores(tokens(q)))
results = {}
def evaluate(name, score_fn, key, qs):
    rr, r1, r5, rr_len = [], 0, 0, []
    l1 = l5 = 0
    ranks_l = []
    for q in qs:
        s = score_fn(q, key)
        order = np.argsort(-s)
        tgt = idx[q["target"]]
        rank = int(np.where(order == tgt)[0][0]) + 1
        lenient = min(int(np.where(order == j)[0][0]) + 1 for j in thread_docs[(q["site"], q["thread"])])
        ranks_l.append(rank); rr.append(1 / rank); r1 += rank <= 1; r5 += rank <= 5; l1 += lenient <= 1; l5 += lenient <= 5
    n = len(qs)
    PER[(name, key, id(qs))] = ([1 / 1 if False else x for x in rr], r1)
    PERR[(name, key, id(qs))] = ranks_l
    return dict(method=name, query_state=key, n_queries=n, recall_at_1=r1 / n, recall_at_5=r5 / n, mrr=sum(rr) / n,
                lenient_recall_at_1=l1 / n, lenient_recall_at_5=l5 / n)
rows = []
PER, PERR = {}, {}
bm_cache = {}
def bm_fn(q, key):
    k = (q["thread"], q["site"], key)
    if k not in bm_cache: bm_cache[k] = bm25_scores(q[key])
    return bm_cache[k]
mini_note = ""
try:
    from sentence_transformers import SentenceTransformer
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=dev)
    D = m.encode([d["text"] for d in docs], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    qe = {}
    for key in ("early", "later"):
        E = m.encode([q[key] for q in queries], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
        for q, e in zip(queries, E): qe[(q["thread"], q["site"], key)] = e
    mini_fn = lambda q, key: D @ qe[(q["thread"], q["site"], key)]
    mini_note = f"device={dev}; max_seq_length={m.max_seq_length} (long queries/answers truncated)"
except Exception as e:  # report NOT RUN honestly
    mini_fn = None; mini_note = f"NOT RUN: {type(e).__name__}: {e}"
for subset_name, qs in (("all_eligible", queries), ("test_split_families", test_q)):
    for key in ("early", "later"):
        for name, fn in (("BM25", bm_fn), ("MiniLM-L6-v2 (pretrained)", mini_fn)):
            if fn is None: continue
            r = evaluate(name, fn, key, qs); r["subset"] = subset_name; rows.append(r)
if rows:
    write_csv(RES / "baseline_results.csv", rows)
# paired bootstrap of later-minus-early (same queries, same corpus)
rng_b = np.random.default_rng(CONFIG["random_seed"])
delta_rows = []
for subset_name, qs in (("all_eligible", queries), ("test_split_families", test_q)):
    for name in ("BM25", "MiniLM-L6-v2 (pretrained)"):
        if (name, "early", id(qs)) not in PERR: continue
        e = np.array(PERR[(name, "early", id(qs))]); l = np.array(PERR[(name, "later", id(qs))])
        for metric, f in (("mrr", lambda r: 1.0 / r), ("recall_at_1", lambda r: (r <= 1).astype(float)), ("recall_at_5", lambda r: (r <= 5).astype(float))):
            d = f(l) - f(e); n = len(d)
            bs = [d[rng_b.integers(0, n, n)].mean() for _ in range(2000)]
            delta_rows.append(dict(subset=subset_name, method=name, metric=metric, n=n, delta_later_minus_early=float(d.mean()),
                                   ci95_lo=float(np.percentile(bs, 2.5)), ci95_hi=float(np.percentile(bs, 97.5))))
if delta_rows: write_csv(RES / "baseline_later_minus_early.csv", delta_rows)
dtxt = chr(10).join(f"* [{r['subset']}] {r['method']} {r['metric']}: later-early = {r['delta_later_minus_early']:+.3f} (95% bootstrap CI {r['ci95_lo']:+.3f}..{r['ci95_hi']:+.3f}, n={r['n']})" for r in delta_rows)
qlen = {k: float(np.mean([len(tokens(q[k])) for q in queries])) for k in ("early", "later")}

# example rankings (3 queries, titles only via ids)
ex = []
for q in queries[:3]:
    s = bm_fn(q, "later"); top = np.argsort(-s)[:3]
    ex.append(f"* thread {q['site']}:{q['thread']} target {q['target']}: BM25(later) top-3 = {[doc_ids[i] for i in top]}")
fm = lambda r: f"{r['method']} | {r['query_state']} | R@1 {r['recall_at_1']:.3f} | R@5 {r['recall_at_5']:.3f} | MRR {r['mrr']:.3f} | lenient R@1 {r['lenient_recall_at_1']:.3f} R@5 {r['lenient_recall_at_5']:.3f}"
body = "\n".join(f"* [{r['subset']}, n={r['n_queries']}] " + fm(r) for r in rows)
(RES / "retrieval_smoke_test.md").write_text(f"""# Retrieval smoke test (PRELIMINARY, automated eligibility, relevance NOT human-verified)

Corpus: {len(docs)} answer documents (same corpus & same candidate set for every query and method); {len(acc)} accepted targets. Queries: {len(queries)} threads with automated >=2 states, no automated leakage flag and an automatically self-contained accepted answer. Strict relevance = accepted answer; lenient = any answer of the same thread (other answers are *unjudged*, not confirmed negatives).
Early/Later query = reconstructed pre-cutoff text (title + initial body [+ first new-fact unit]); mean tokens early {qlen['early']:.0f} vs later {qlen['later']:.0f}.
MiniLM: {mini_note}

{body}

### Paired later-minus-early (bootstrap, 2000 resamples)
{dtxt}

## Caveats / failures
* The query is a full question body and the answer is a different post: lexical overlap (BM25) is expected to be strong; a later > early gain may partly be query length, not information.
* Eligible set is selected by an automated filter that may favour threads with verbose askers; selection bias is not quantified.
* Only {len(queries)} queries from a 2x2000-thread pool; no variance across runs/seeds; no FT arm was run (FT-Aware, FT-Random, FT-Full are NOT RUN by design).
* Example rankings:
{chr(10).join(ex)}
* Reproduce: `python -I pilot/stackexchange_raw/scripts/04_retrieval_smoke.py`
""", encoding="utf8")
print(body); print(mini_note); print("elapsed", time.time() - t0)
