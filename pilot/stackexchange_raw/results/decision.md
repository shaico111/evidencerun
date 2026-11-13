# Decision — Stack Exchange raw source for EvidenceRun: Symptom-Aware Solution Retrieval

**CONDITIONAL GO — for a two-state (Early/Later) offline retrospective benchmark on Ask Ubuntu + Server Fault. NOT supported yet: a three-stage design, an Observability factor, or any claim that FT-Aware helps.** All human gates are PENDING; every rate below is automated unless stated.

## Gate table (observed numbers first; thresholds are project-management proposals)
| Gate | Observed | Status |
|---|---|---|
| Availability (source, history, accepted IDs, terms) | Dumps downloaded, SHA-1 matches IA manifest; PostHistory present for 100% of 53,158 / 42,424 Stage-A frame threads (4 SF threads lack initial body); accepted IDs resolve (AU 136,151/136,162; SF 153,246/153,269). Licence: CC BY-SA, but permitted use for model training / redistribution of the 2024-era dump is **unresolved** | Technical GO; legal **UNKNOWN** |
| Genuine progression ≥25% have 2+ states | Automated: AU 39.2% (CI 37.1–41.4), SF 37.1% (35.1–39.3) of pool n=2000. LLM-assisted precision of that flag on 20 unseen rows: 16/20 = 80% (CI 58–92). Crude precision-adjusted range ≈ 22–36% | Provisional PASS; lower bound touches threshold; false negatives unmeasured |
| 3+ states ≥10% | Automated AU 15.5%, SF 12.8% (leak-free & self-contained: 10.9%, 10.1%); 3+ precision NOT measured | **Unverified / borderline** → optional only |
| 2+ with relevant self-contained answer ≥70% | Automated self-contained among 2+: AU 74.9% (71.8–77.8), SF 81.4% (78.5–84.1). Relevance: LLM-assisted 19/20 yes + 1 partial. **Human: PENDING** | Provisional PASS |
| Scale ≥1,000 eligible, ≥500 distinct targets | Projected (automated, unadjusted) ≥2 & self-contained & leak-free: AU 14.6–16.7k, SF 12.0–13.7k; pool already has 588 + 605 distinct targets | PASS on count (even at 50% precision); quality unverified |
| Leakage | Rule flags: AU 12.2%, SF 9.2% of pool. LLM-assisted spot check found 1 miss in 20 (fixed + unit-tested afterwards, residual unknown). 27% of accepted answers are written by the asker (hindsight). 83% / 78% accepted = first answer (cutoff conservative) | **CONDITIONAL** — needs human confirmation |
| Independent evaluation ≥100 human-reviewed held-out states | Review queue (200 random + 200 stratified rows) and guidelines ready; **0 human reviews done** | **PENDING** |
| Observability | No labels produced, no agreement measured | **NOT ASSESSED** → drop or make a clearly secondary add-on |
| Novelty / workload | Gap plausible (limited search); BUT pretrained retrieval barely benefits from the "later" state: MRR +0.013 (CI +0.004..+0.021) MiniLM, +0.012 (+0.001..+0.024) BM25, n=1193 | **At risk** (see below) |

## Self-review (attacking our own conclusion)
* *2–3 states = new facts or just messages?* Automated filter is heuristic; unseen LLM-assisted check: 16/20 genuine, 2 false (clarification/ack, how-to edit), 2 uncertain. Not human. Rules were tightened three times after looking at data (request-for-clarification, resolution regex, @username digits) — the audit sample (n=100/site) was used for development, so its rates are not clean hold-outs; the pool and the 20-row check are less affected but the final rules were applied after that check.
* *Retrospective revisions counted as earlier?* No: early text is rebuilt from PostHistory type 2; the final body had ≥5 additional token types in 46.2% (AU) / 42.2% (SF) of pool threads, so using final text would have leaked edits. Caveat: PostHistory text is Markdown while Posts.Body is HTML — comparisons use tokens.
* *Answer before the "later" observation?* Cutoff = first answer; units at/after it are dropped; equal timestamps abstain; tests cover it. Comment timestamps are only for comments that still exist in the dump (deleted comments invisible) — cannot be excluded as a bias.
* *AcceptedAnswerId a useful standalone solution?* Auto-self-contained 88–90%, but 27% are asker self-answers (often "I figured it out…") and ~80% are the first answer; relevance not human-verified. 4 of the 41 reviewed threads were not troubleshooting questions (lexical filter).
* *Biased filters?* Stage-A requires a pre-answer comment/edit, which selects threads with early interaction; the share of ALL accepted-answer threads is 53,158/136,151 = 39% (AU), 42,424/153,246 = 28% (SF). Negatives were not human-audited.
* *Train/test overlap?* No training run. Split frozen by answer family (0 near-duplicate answer pairs at TF-IDF cosine ≥0.9 among 4,000). Question-level paraphrase duplicates not audited.
* *Same candidate set for all baselines?* Yes (6,566 docs, same queries).
* *Could a model win by query length / copy-overlap?* Yes — later queries are longer; the small gain cannot be attributed to information vs length. Also queries are the full question body, answers often repeat its vocabulary; MiniLM R@1 ≈ 0.48 already at "early".
* *Stage independent of Observability?* Observability unlabelled, so independence is untested; Stage here is partly a renamed timestamp ordering of asker-supplied additions.
* *Differs from generic Stack Exchange ranking?* Only through the prefix-state construction and the Aware-vs-Random controlled training, not the retrieval task.
* *Any number human-verified?* **No.** Three evidence levels used: automated; LLM-assisted (single reviewer = this assistant, 41 rows listed in annotations/llm_assisted_review.csv); human = none.
* *Would a skeptic say NO-GO with the same counts from a competing dataset?* On scale/availability no; on the central hypothesis a skeptic would point to the +0.013 MRR early→later headroom and to the unverified human gates. Hence CONDITIONAL, not GO.

## Recommendation
1. Proceed with this source **only as Early/Later** primary design; keep 3-state as an optional subset; drop Observability unless two humans can label it.
2. Before any training: human-review ≥30 rows/site (+≥20 doubly reviewed) from `annotations/human_review_queue.csv`; confirm leakage precision/recall and relevance; settle licence/terms question.
3. If the human review shows < ~60% genuine second states, or if a fine-tuned arm cannot beat the +0.013 early→later headroom in a matched-budget pilot, reduce to a different design (e.g., use asker-comment clarification as Qulac-style turns) or a different source.
Do not run full fine-tuning until step 2 is complete.
