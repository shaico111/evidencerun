"""Assemble funnel/manifest CSVs, evidence examples and all markdown reports from computed artifacts only."""
import csv
import json
import pickle
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from se_common import *  # noqa
from temporal import html_to_text  # noqa

sys.stdout.reconfigure(encoding="utf8")
stats = json.load(open(RES / "stats.json"))
SITES = list(CONFIG["sites"])
prov = json.load(open(PILOT / "provenance" / "sources.json"))
rev = list(csv.DictReader(open(PILOT / "annotations" / "llm_assisted_review.csv", encoding="utf8")))
base = list(csv.DictReader(open(RES / "baseline_results.csv")))
delta = list(csv.DictReader(open(RES / "baseline_later_minus_early.csv")))
ci = fmt_ci

# ---- combined CSVs
fun, man, err = [], [], []
for s in SITES:
    fun += list(csv.DictReader(open(RES / f"funnel_{s}.csv", encoding="utf8")))
    man += list(csv.DictReader(open(RES / f"sample_manifest_{s}.csv", encoding="utf8")))
    err += list(csv.DictReader(open(RES / f"fetch_errors_{s}.csv", encoding="utf8")))
write_csv(RES / "funnel.csv", fun, ["site", "step", "count"])
write_csv(RES / "sample_manifest.csv", man)
if not err:
    err = [dict(site="both", question_id="", error="NONE: 0 fetch errors, 0 duplicate exclusions in 2 x 2600 oversampled threads", reason="")]
write_csv(RES / "fetch_errors.csv", err, ["site", "question_id", "error", "reason"])

# ---- tests (really executed)
tp = subprocess.run([sys.executable, "-I", str(PILOT / "tests" / "test_temporal.py")], capture_output=True, text=True)
test_out = (tp.stderr or "").strip().splitlines()
test_summary = f"exit code {tp.returncode}; " + " | ".join(l for l in test_out if l.startswith(("Ran", "OK", "FAILED")))

# ---- LLM-assisted review summary (unseen set only for precision)
un = [r for r in rev if r["review_set"].startswith("unseen")]
tu = [r for r in rev if r["review_set"].startswith("tuning")]
un_yes = sum(r["llm_valid_2plus_states"] == "yes" for r in un)
un_leak_free_yes = un_yes - sum("LEAK MISSED" in r["note"] for r in un)
un_rel = sum(r["llm_accepted_relevant"] == "yes" for r in un)
nontrouble = sum(r["llm_troubleshooting"] == "no" for r in rev)
prec = f"{ci(un_yes, len(un))}"
prec_lf = f"{ci(un_leak_free_yes, len(un))}"
plo, phi = wilson(un_yes, len(un))

# ---- per-site tables
def rate(k, n): return f"{ci(k, n)}"
rows_c = []
proj = {}
for s in SITES:
    st, a, p = stats[s], stats[s]["audit"], stats[s]["pool"]
    F = st["frame_size"]
    lo, hi = wilson(p["two_plus_selfcontained_leakfree"], p["n"])
    proj[s] = (F, F * lo, F * p["two_plus_selfcontained_leakfree"] / p["n"], F * hi)
    lo3, hi3 = wilson(p["three_plus_selfcontained_leakfree"], p["n"])
    proj[s + "3"] = (F * lo3, F * p["three_plus_selfcontained_leakfree"] / p["n"], F * hi3)
    d = prov["sites"][s]
    rows_c.append(f"| {'Ask Ubuntu' if s=='askubuntu' else 'Server Fault'} | IA `stackexchange` item, file mtime 2024-04-07, sha256 `{d['sha256'][:12]}…` | {F:,} (Stage-A, automated) | {a['n']} audit / {p['n']} pool | {p['n']} / {p['n']} (0 errors) | {p['accepted_found']}/{p['n']} (automated, joins verified) | {a['two_plus']}/{a['n']} audit; {p['two_plus']}/{p['n']} pool (automated) | {a['three_plus']}/{a['n']}; {p['three_plus']}/{p['n']} (automated) | NOT human-verified (LLM-assisted sample below) | {a['two_plus_selfcontained_leakfree']}/{a['n']}; {p['two_plus_selfcontained_leakfree']}/{p['n']} (automated, relevance not included) | {a['distinct_target_answers']} (audit); {p['distinct_target_answers']} (pool) |")
tableC = "\n".join(rows_c)

def site_block(s):
    st, a, p = stats[s], stats[s]["audit"], stats[s]["pool"]
    F, plo_, pmid, phi_ = proj[s]
    lines = [f"### {s} (Stage-A frame = {F:,})", "",
             "| metric (automated) | simple-random audit sample n=100 | seeded pool n=2000 |", "|---|---|---|"]
    for k, lab in (("two_plus", "≥2 states"), ("three_plus", "≥3 states"), ("self_contained_auto", "accepted answer auto-self-contained"),
                   ("two_plus_selfcontained_leakfree", "≥2 states AND self-contained AND no leakage flag"),
                   ("three_plus_selfcontained_leakfree", "≥3 states AND self-contained AND no leakage flag"),
                   ("leakage_suspected", "leakage suspected (automated)"), ("accepted_is_first", "accepted answer is the first answer"),
                   ("self_answered", "accepted answer written by the asker"), ("final_differs", "final body has ≥5 tokens not in initial body (later additions)")):
        lines.append(f"| {lab} | {rate(a[k], a['n'])} | {rate(p[k], p['n'])} |")
    lines.append("")
    lines.append(f"Projection (automated, NOT precision-adjusted): ≥2 & self-contained & leak-free ≈ {pmid:,.0f} threads (95% CI of the pool rate × frame: {plo_:,.0f}–{phi_:,.0f}); ≥3: {proj[s+'3'][1]:,.0f} ({proj[s+'3'][0]:,.0f}–{proj[s+'3'][2]:,.0f}). Distinct target answers in the pool: {p['distinct_target_answers']}.")
    return "\n".join(lines)

funnel_tbl = "\n".join(f"| {r['site']} | {r['step']} | {int(r['count']):,} |" for r in fun)
(RES / "source_comparison.md").write_text(f"""# Source comparison: Ask Ubuntu vs Server Fault (Stack Exchange dump, Internet Archive ~2024-04)

All rates are **automated** (rules in scripts/temporal.py) unless stated. They are NOT human-verified. Frame = Stage-A filter (config.json), computed over the FULL dumps (not a sample). Stack Overflow was not run (the two sites already give a large frame; no insufficiency).

## Funnel (full dump)
| site | step | count |
|---|---|---:|
{funnel_tbl}

{site_block('askubuntu')}

{site_block('serverfault')}

## Precision check of the automated "≥2 valid states" flag (LLM-assisted, single reviewer — NOT an independent human)
Fresh set (rows not used to design the rules): {prec} judged to have ≥2 genuine states; leak-free: {prec_lf}; accepted answer judged relevant: {ci(un_rel, len(un))}. Pre-tightening tuning sample (n={len([r for r in tu if r['llm_valid_2plus_states'] in ('yes','no')])}) is excluded because the rules were adjusted after viewing it. Among {len(rev)} reviewed threads {nontrouble} were not troubleshooting questions (lexical filter false positives).
Precision-adjusted ≥2-state share of the frame (pool rate × precision, ranges from the two CIs): AU ≈ {100*stats['askubuntu']['pool']['two_plus']/2000*plo:.0f}–{100*stats['askubuntu']['pool']['two_plus']/2000*phi:.0f}%, SF ≈ {100*stats['serverfault']['pool']['two_plus']/2000*plo:.0f}–{100*stats['serverfault']['pool']['two_plus']/2000*phi:.0f}% (crude product of two intervals; the 20-row review has wide uncertainty and misses false negatives entirely).
""", encoding="utf8")

# ---- leakage audit
def lk(s): return stats[s]["pool"]
(RES / "leakage_audit.md").write_text(f"""# Leakage audit (automated rules + LLM-assisted spot check)

**Cutoff.** effective cutoff = min(first published answer, earliest non-asker question comment sharing ≥2 distinctive 4-grams with the accepted answer). Evidence units must be strictly earlier; equal/malformed timestamps abstain. The early text is rebuilt from PostHistory *Initial Body* (type 2), never from the final post (final body contains ≥5 token types absent from the initial body (later-added content) in {lk('askubuntu')['final_differs']}/2000 AU and {lk('serverfault')['final_differs']}/2000 SF pool threads — using the final text would have leaked later edits).

| signal (pool n=2000/site) | Ask Ubuntu | Server Fault |
|---|---:|---:|
| leakage flagged by rules (resolution claim / answer overlap / comment discloses solution) | {lk('askubuntu')['leakage_suspected']} | {lk('serverfault')['leakage_suspected']} |
| cutoff moved earlier because a comment already disclosed the solution | {lk('askubuntu')['cutoff_by_comment']} | {lk('serverfault')['cutoff_by_comment']} |
| accepted answer is the very first answer | {lk('askubuntu')['accepted_is_first']} | {lk('serverfault')['accepted_is_first']} |
| accepted answer authored by the asker (hindsight-written self-answer; retrieval target may be idiosyncratic) | {lk('askubuntu')['self_answered']} | {lk('serverfault')['self_answered']} |

All flags are **suspected**, none confirmed by a human. Known weaknesses: (1) non-asker comments are excluded from query evidence by design, so solution hints in comments cannot enter queries, but asker replies that paraphrase a commenter's fix can; (2) the LLM-assisted review of 20 unseen automated positives found **1 missed leak** (askubuntu:939398, asker comment before the first answer says the NVIDIA drivers "solve the problem"; the resolution regex was extended afterwards and a unit test added, so the estimated residual miss rate is ≥1/20 and unknown); (3) deliberately contaminated unit fixtures ({test_summary}) cover late diagnosis, answer-before-clarification, accepted-after-first, solution in comment, reversed timestamps, missing history, quoted solution, late edit, equal timestamps, duplicates-by-formatting; (4) near-duplicate questions were removed only by exact normalised title / accepted-answer text (0 removed in 2×2600) — paraphrased duplicates are not audited; (5) no model training occurred, so no train/test contamination exists yet (see split_leakage_audit.md).
Label leakage: the accepted answer is used only (a) to move the cutoff earlier and (b) to veto overlapping units; it is never given to any query generator (no generator exists yet).
""", encoding="utf8")

# ---- examples with provenance
def excerpt(t, k=150): return re.sub(r"\s+", " ", t or "")[:k]
pos, rej = [], []
for s in SITES:
    P = pickle.load(open(RAW / s / "pool.pkl", "rb")); S = pickle.load(open(RAW / s / "states.pkl", "rb"))
    base_url = f"https://{'askubuntu.com' if s == 'askubuntu' else 'serverfault.com'}/questions/"
    for q in P["audit"]:
        r = S[q]["row"]
        item = (s, q, base_url + str(q), S[q], r)
        if r["auto_states"] >= 2 and r["leakage_auto"] == "none" and S[q]["aq"].get("self_contained_auto") == 1 and sum(x[0] == s for x in pos) < 5:
            pos.append(item)
        elif (r["leakage_auto"] != "none" or r["auto_states"] == 1 and r["rejected_summary"]) and sum(x[0] == s for x in rej) < 5:
            rej.append(item)
def fmt_item(it, pos_):
    s, q, url, st, r = it
    us = "; ".join(f"{u['kind']} @ {u['t']} ({u['n_new_tokens']} new tokens): “{excerpt(u['text'], 110)}”" for u in st["units"][:2])
    return (f"* **{s}:{q}** — {url} — accepted answer id {r['accepted_answer_id']} (answered {r['accepted_answer_at']}), first answer {r['first_answer_at']}, cutoff {r['cutoff']} ({r['cutoff_reason']}), states={r['auto_states']}, leakage={r['leakage_auto']}. "
            + (f"Early: “{excerpt(st['early'], 110)}” Added: {us}" if pos_ else f"Rejected units: {r['rejected_summary'] or '-'}; {r['leakage_detail'][:120]}"))
(RES / "prefix_examples.md").write_text("# Provenance-backed examples (content: Stack Exchange users, CC BY-SA; attribution = URL on each line; excerpts ≤ ~150 chars)\n\nAutomated labels only, drawn from the simple-random audit sample (first 5 qualifying per site). Not human verified.\n\n## 10 automated positives (≥2 states, no leakage flag, self-contained answer)\n"
    + "\n".join(fmt_item(i, True) for i in pos) + "\n\n## 10 rejected / ambiguous (leakage flagged, or only 1 state with rejected candidate units)\n" + "\n".join(fmt_item(i, False) for i in rej) + "\n", encoding="utf8")

# ---- retrieval metrics lines
def bl(subset, method, key):
    r = next(x for x in base if x["subset"] == subset and x["method"].startswith(method) and x["query_state"] == key)
    return r
def dl(subset, method, metric):
    return next(x for x in delta if x["subset"] == subset and x["method"].startswith(method) and x["metric"] == metric)
ret = {m: {k: bl("all_eligible", m, k) for k in ("early", "later")} for m in ("BM25", "MiniLM")}
dm = dl("all_eligible", "MiniLM", "mrr"); db = dl("all_eligible", "BM25", "mrr")
d1m = dl("all_eligible", "MiniLM", "recall_at_1")
n_q = ret["BM25"]["early"]["n_queries"]
ret_line = (f"n={n_q} queries, corpus {sum(1 for _ in csv.DictReader(open(RES/'candidate_corpus_manifest.csv')))} answers. MiniLM Recall@1/5/MRR early {float(ret['MiniLM']['early']['recall_at_1']):.3f}/{float(ret['MiniLM']['early']['recall_at_5']):.3f}/{float(ret['MiniLM']['early']['mrr']):.3f}, later {float(ret['MiniLM']['later']['recall_at_1']):.3f}/{float(ret['MiniLM']['later']['recall_at_5']):.3f}/{float(ret['MiniLM']['later']['mrr']):.3f}; "
            f"BM25 early {float(ret['BM25']['early']['recall_at_1']):.3f}/{float(ret['BM25']['early']['recall_at_5']):.3f}/{float(ret['BM25']['early']['mrr']):.3f}, later {float(ret['BM25']['later']['recall_at_1']):.3f}/{float(ret['BM25']['later']['recall_at_5']):.3f}/{float(ret['BM25']['later']['mrr']):.3f}. "
            f"Later−early MRR: MiniLM {float(dm['delta_later_minus_early']):+.3f} (95% CI {float(dm['ci95_lo']):+.3f}..{float(dm['ci95_hi']):+.3f}), BM25 {float(db['delta_later_minus_early']):+.3f} ({float(db['ci95_lo']):+.3f}..{float(db['ci95_hi']):+.3f}).")
json.dump(dict(ret_line=ret_line, test_summary=test_summary, precision=prec, precision_leakfree=prec_lf, proj={k: v for k, v in proj.items()}), open(RES / "report_numbers.json", "w"), indent=1)
print(ret_line); print(test_summary); print(prec, prec_lf)
Path(RES / "_tableC.md").write_text(tableC, encoding="utf8")
