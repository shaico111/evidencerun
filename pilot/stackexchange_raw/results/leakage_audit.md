# Leakage audit (automated rules + LLM-assisted spot check)

**Cutoff.** effective cutoff = min(first published answer, earliest non-asker question comment sharing ≥2 distinctive 4-grams with the accepted answer). Evidence units must be strictly earlier; equal/malformed timestamps abstain. The early text is rebuilt from PostHistory *Initial Body* (type 2), never from the final post (final body contains ≥5 token types absent from the initial body (later-added content) in 924/2000 AU and 843/2000 SF pool threads — using the final text would have leaked later edits).

| signal (pool n=2000/site) | Ask Ubuntu | Server Fault |
|---|---:|---:|
| leakage flagged by rules (resolution claim / answer overlap / comment discloses solution) | 243 | 184 |
| cutoff moved earlier because a comment already disclosed the solution | 113 | 77 |
| accepted answer is the very first answer | 1658 | 1555 |
| accepted answer authored by the asker (hindsight-written self-answer; retrieval target may be idiosyncratic) | 543 | 555 |

All flags are **suspected**, none confirmed by a human. Known weaknesses: (1) non-asker comments are excluded from query evidence by design, so solution hints in comments cannot enter queries, but asker replies that paraphrase a commenter's fix can; (2) the LLM-assisted review of 20 unseen automated positives found **1 missed leak** (askubuntu:939398, asker comment before the first answer says the NVIDIA drivers "solve the problem"; the resolution regex was extended afterwards and a unit test added, so the estimated residual miss rate is ≥1/20 and unknown); (3) deliberately contaminated unit fixtures (exit code 0; Ran 20 tests in 0.004s | OK) cover late diagnosis, answer-before-clarification, accepted-after-first, solution in comment, reversed timestamps, missing history, quoted solution, late edit, equal timestamps, duplicates-by-formatting; (4) near-duplicate questions were removed only by exact normalised title / accepted-answer text (0 removed in 2×2600) — paraphrased duplicates are not audited; (5) no model training occurred, so no train/test contamination exists yet (see split_leakage_audit.md).
Label leakage: the accepted answer is used only (a) to move the cutoff earlier and (b) to veto overlapping units; it is never given to any query generator (no generator exists yet).
