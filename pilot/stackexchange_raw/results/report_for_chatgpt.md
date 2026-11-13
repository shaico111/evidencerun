# EvidenceRun — Stack Exchange raw-data validation pilot: report (for independent review)
Generated 2026-11-13 by Claude Code (Sonnet 5.5). **This report has NOT been validated by ChatGPT or by any independent human.** Evidence levels: *automated* (rules), *LLM-assisted* (this assistant, single pass), *human* (none yet).

## A. Executive verdict
**CONDITIONAL GO** for EvidenceRun: Symptom-Aware Solution Retrieval on Stack Exchange raw dumps (Ask Ubuntu + Server Fault), restricted to a **two-state Early/Later offline retrospective** design. The data are large (Stage-A frames of 53,158 and 42,424 threads; about 37–39% automatically show ≥2 pre-answer states) and temporally reconstructable from PostHistory. It preserves the course novelty only partially: with pretrained models the "later" state improves MRR by just +0.013 (95% CI +0.004..+0.021), so the headroom for FT-Aware vs FT-Random is small and unproven; Observability and three-stage claims are unsupported. Everything human-dependent (annotation, kappa, licence for training use) is PENDING.

## B. Git and reuse
* Repo https://github.com/shaico111/evidencerun ; original local branch `poc/dataset-feasibility-pilot` (verified present, tip `dacb9aa`); new branch **`poc/stackexchange-raw-validation`**, base SHA `dacb9aa00d1226300774e3b182e344190cbfa3b3` (the only commit containing the earlier pilot assets). Final commit SHA and final `git status`: given in the final reply (a commit cannot contain its own hash). **Not pushed.** Pre-existing untracked zips (`docs.zip`, `pilot.zip`, …) were left untouched and uncommitted.
* KEEP/ARCHIVE: the whole GitLab/Wikimedia/MANtIS pilot (read-only; a `git diff` against `dacb9aa` over its paths is empty). ADAPT later: README/WORK_PLAN/TASKS. REPLACE for the new source: old fetchers. No retrieval/training code existed to reuse. Table: `docs/stackexchange_migration_audit.md`.
* New files: `docs/stackexchange_migration_audit.md`; `pilot/stackexchange_raw/{README.md,config.json}`, `scripts/{se_common,temporal,01..05}*.py`, `tests/test_temporal.py`, `provenance/sources.json`, `annotations/{annotation_guidelines.md,human_review_queue.csv,llm_assisted_review.csv}`, `results/*` (listed in I). Modified: `.gitignore` (+raw dir).

## C. Data extraction table
All automated unless stated. pool = seeded random sample n=2000/site drawn from the full Stage-A frame; audit = its first 100 rows (simple random).

| Site | Dump | Accessible frame | Sampled | Fetched | Accepted answer found | 2+ meaningful states | 3+ states | Verified relevant answer | 2+ AND relevant AND leak-free | Distinct target answers |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| Ask Ubuntu | Internet Archive `stackexchange` item, file dated 2024-04-07 (sha256 59632526…); full frame counted | 53,158 (of 136,151 accepted-resolvable) — automated | 100 audit / 2000 pool | 2000/2000, 0 errors | 2000/2000 (joins verified, automated) | pool 785 = 39.2% (CI 37.1–41.4); audit 42/100 | pool 310 = 15.5% (14.0–17.2); audit 16/100 | **human: NOT DONE**; LLM-assisted: see below | pool 588 = 29.4% (27.4–31.4); "relevant" here = automated self-contained only; audit 31/100 | 588 (pool) |
| Server Fault | same item (sha256 8a2fed86…) | 42,424 (of 153,246) — automated | 100 / 2000 | 2000/2000, 0 errors | 2000/2000 | pool 743 = 37.1% (35.1–39.3); audit 37/100 | pool 257 = 12.8% (11.5–14.4); audit 7/100 | human: NOT DONE | pool 605 = 30.2% (28.3–32.3); audit 28/100 | 605 (pool) |
| Stack Overflow | NOT RUN (two sites sufficed for the gate; would need a separate denominator) | – | – | – | – | – | – | – | – | – |

Precision of the "≥2 states" flag (LLM-assisted, 20 unseen auto-positive rows, both sites mixed): 16/20 = 80% (CI 58–92); leak-free 15/20 = 75% (53–89); accepted answer judged relevant 19/20 (+1 partial). Funnel: `results/funnel.csv`. Projection (automated, not precision-adjusted) of ≥2 & self-contained & leak-free: AU ≈ 15.6k (14.6–16.7k), SF ≈ 12.8k (12.0–13.7k); 3+: AU ≈ 5.8k, SF ≈ 4.3k. Precision-adjusted share of the frame with ≥2 states ≈ 22–36% (crude product of two intervals; false negatives not measured).

## D. Case studies (excerpts ≤ ~130 chars, CC BY-SA, source URL given; labels automated / LLM-assisted)
Strongest:
1. https://askubuntu.com/questions/670960 — Xubuntu login loop. Asker edit 2015-09-06 15:25 adds `.xsession-errors` output; asker edit 2015-09-07 16:17 adds `echo $PATH` showing a user `~/bin` first; first answer 2015-09-08 12:55 is the accepted answer 671718 (not a self-answer) and diagnoses a stray `~/bin` shadowing commands. Two genuine pre-cutoff observations; answer relevant.
2. https://serverfault.com/questions/493028 — CentOS 6.4 missing route on boot. Edits 13:54 (`route -n` output) and 14:00 (`ifcfg-eth0`) precede the first answer 14:04 (accepted 493212 at 14:05). Relevant.
3. https://askubuntu.com/questions/735901 — Eclipse icon not shown. Asker comments 20:03 ("Changing to /opt/eclipse/eclipse doesn't fix it…") and 20:23 (paper icon; question mark on dock) precede first answer 20:33 (accepted 735924), which points at a stale `eclipse.desktop`.
Failures:
4. https://askubuntu.com/questions/939398 — a leak MISSED by the first rule version: an asker comment before the first answer says the NVIDIA drivers "solve the problem" (resolution claim). The regex was extended afterwards (now rejected and flagged); shows residual miss risk.
5. https://askubuntu.com/questions/1244128 — still a false positive: asker comments about checksum/download access were counted as states, none is a symptom; the accepted answer is the asker's own ("corrupted .bin, downloaded again") → hindsight target.
6. https://serverfault.com/questions/1127879 — false positive and not troubleshooting: the edit adds "I could do a dumb copy/paste… there's a better way"; a how-to question.
More: `results/prefix_examples.md` (10 automated positives + 10 rejected/ambiguous, with IDs, timestamps, cutoffs).

## E. Data leakage and target quality (`results/leakage_audit.md`)
Rule flags (suspected, none confirmed): AU 243/2000 (12.2%), SF 184/2000 (9.2%); cutoff moved earlier by a solution-disclosing comment: 113 / 77. LLM-assisted spot check: 1 missed leak in 20 (fixed afterwards). Accepted answer is the first answer: 82.9% / 77.8%; written by the asker (hindsight): 27.1% / 27.8%; automated self-contained: 87.8% / 89.8%; missing history: 4 SF threads lack an initial body, 0 AU. Duplicates: 0 exact title/answer duplicates removed among 2×2600 oversampled threads; 0 near-duplicate accepted-answer pairs (TF-IDF cosine ≥0.9, 4,000 answers). Incorrect-accepted-answer and multi-answer ambiguity rates: **NOT MEASURED** (need humans). Using the final post text would have leaked later additions in 46.2% / 42.2% of threads, hence history-based reconstruction (comments that were deleted are invisible in the dump — a bias that cannot be excluded).

## F. Course compliance and novelty (`results/course_alignment.md`, `results/novelty_review.md`)
Guides read: proposal / midterm / final / GitHub-submission pages at apartsin.com (no point weights or dates on them; the "Project Requirements" and "Assessment Criteria" pages were not read — a risk). Met in this pilot: real data, BM25 and pretrained baselines, end-to-end + component audits, honest scope. Not yet: a fine-tuned model (hard requirement), synthetic data with QC, ≥100 human-reviewed independent eval states. Related work (7 listed), e.g. Qulac https://arxiv.org/abs/1907.06554 ; mixed-initiative reformulation https://arxiv.org/abs/2307.08803 ; TechQA-based QA https://arxiv.org/abs/2010.09780 ; BEIR/CQADupStack https://arxiv.org/abs/2104.08663 ; typo-robust dense retrieval https://arxiv.org/abs/2306.10348 . The gap is claimed only in hedged form (short search): retriever training on source-grounded, time-ordered partial states with an Aware-vs-Random control. Generic Stack Exchange answer retrieval is NOT novel. No claim of course/lecturer approval is made.

## G. Retrieval sanity check (PRELIMINARY; automated eligibility; relevance unverified)
Corpus 6,566 answer documents (4,000 accepted targets + 2,566 other answers of the same threads, "unjudged"), identical for every query and method; 1,193 automated-eligible queries. Strict relevance = accepted answer.

| method | query state | R@1 | R@5 | MRR |
|---|---|---:|---:|---:|
| BM25 | early | 0.272 | 0.427 | 0.348 |
| BM25 | later | 0.282 | 0.448 | 0.360 |
| MiniLM-L6-v2 (pretrained, CPU, 256-token truncation) | early | 0.478 | 0.732 | 0.591 |
| MiniLM-L6-v2 | later | 0.492 | 0.743 | 0.604 |

Later−early MRR (paired bootstrap, 2000 resamples): MiniLM +0.013 (+0.004..+0.021), BM25 +0.012 (+0.001..+0.024). The held-out answer-family subset (n=371) is similar (`baseline_results.csv`). Caveats: later queries are longer; the query is the whole question body; truncation; one run, no seeds; lenient (any answer of the thread) metrics are in the CSV. **FT-Full, FT-Random, FT-Aware, Stage-only: NOT RUN (by design).**

## H. Decision and next 3 actions
Keep from the old repo: history, plan, seed and Wilson conventions; archive the runbook pilot. Proceed with this source **as Early/Later**; make Stage-only primary; drop Observability unless humans label it (agreement unmeasured). Highest risk: the small measured early→later headroom plus unverified human gates and the unresolved training-use licence. Ranked next actions: (1) two humans review ≥30 rows/site (≥20 doubly) from `annotations/human_review_queue.csv`, compute kappa, confirm precision and leakage; (2) resolve licence/terms for training use and redistribution; (3) only if (1) shows ≥~60% genuine second states, run a ≤10-minute matched-budget contrastive smoke test (FT-Random vs FT-Aware). No full training recommended before that.

## I. Reproducibility and attachment manifest
Environment: Windows 11, Python 3.12.10, py7zr 1.1.4, rank-bm25 0.2.2, sentence-transformers (torch 2.15, CPU), numpy 2.5.4. Seed 42 (`config.json`). Commands: `pilot/stackexchange_raw/README.md`. Tests really executed: exit code 0, 20 tests OK, 0 skipped. Hashes: `provenance/sources.json` (SHA-1 equals the IA manifest for both archives). Wall-clock: frame+fetch ≈ 2 min/site, audit ≈ 1 min, retrieval ≈ 8 min (CPU). Raw data (several GB incl. extracted XML) stay under the gitignored `pilot/stackexchange_raw/raw/`. Pending human steps: annotation, kappa, licence review, Observability labelling.
Attach: `results/{decision,source_comparison,leakage_audit,split_leakage_audit,retrieval_smoke_test,course_alignment,novelty_review,migration_summary,prefix_examples}.md`, `results/{funnel,sample_manifest,fetch_errors,timeline_audit,accepted_answer_quality,candidate_corpus_manifest,baseline_results,baseline_later_minus_early}.csv`, `results/stats.json`, `provenance/sources.json`, `annotations/{annotation_guidelines.md,human_review_queue.csv,llm_assisted_review.csv}`.
