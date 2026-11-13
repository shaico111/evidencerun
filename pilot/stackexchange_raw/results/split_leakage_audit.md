# Split / near-duplicate leakage audit (automated)

* Candidate corpus: 6566 answer documents (4000 accepted targets, one per sampled thread; remaining are other answers of the same threads, labelled `unjudged`).
* Near-duplicate families among accepted answers: TF-IDF cosine >= 0.9 -> 0 pairs, 0 families with >1 member, largest family size 1.
* Split frozen **by answer family** with a hash of (seed 42, family id) before any query/metric computation: 1205 test / 2795 train accepted targets (30% test target).
* All eligible queries (1193) are evaluated for the smoke test (no training here), and the test-split subset (371) is reported separately. This is the *held-out solution family* split (harder than held-out question). Held-out-question-only was not separately run.
* Not audited: near-duplicate *questions* across families (only exact normalised-title / accepted-answer duplicates were removed at sampling; see fetch_errors_*.csv), paraphrased duplicates, and cross-site duplicates. Human review pending.
* Training contamination: **no training was run**; therefore no train/test contamination can have occurred in this pilot, and this audit only prepares the split.
