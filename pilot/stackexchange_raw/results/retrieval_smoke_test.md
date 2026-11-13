# Retrieval smoke test (PRELIMINARY, automated eligibility, relevance NOT human-verified)

Corpus: 6566 answer documents (same corpus & same candidate set for every query and method); 4000 accepted targets. Queries: 1193 threads with automated >=2 states, no automated leakage flag and an automatically self-contained accepted answer. Strict relevance = accepted answer; lenient = any answer of the same thread (other answers are *unjudged*, not confirmed negatives).
Early/Later query = reconstructed pre-cutoff text (title + initial body [+ first new-fact unit]); mean tokens early 174 vs later 243.
MiniLM: device=cpu; max_seq_length=256 (long queries/answers truncated)

* [all_eligible, n=1193] BM25 | early | R@1 0.272 | R@5 0.427 | MRR 0.348 | lenient R@1 0.339 R@5 0.493
* [all_eligible, n=1193] MiniLM-L6-v2 (pretrained) | early | R@1 0.478 | R@5 0.732 | MRR 0.591 | lenient R@1 0.615 R@5 0.796
* [all_eligible, n=1193] BM25 | later | R@1 0.282 | R@5 0.448 | MRR 0.360 | lenient R@1 0.347 R@5 0.512
* [all_eligible, n=1193] MiniLM-L6-v2 (pretrained) | later | R@1 0.492 | R@5 0.743 | MRR 0.604 | lenient R@1 0.630 R@5 0.806
* [test_split_families, n=371] BM25 | early | R@1 0.305 | R@5 0.461 | MRR 0.378 | lenient R@1 0.375 R@5 0.507
* [test_split_families, n=371] MiniLM-L6-v2 (pretrained) | early | R@1 0.488 | R@5 0.749 | MRR 0.605 | lenient R@1 0.596 R@5 0.792
* [test_split_families, n=371] BM25 | later | R@1 0.326 | R@5 0.499 | MRR 0.401 | lenient R@1 0.394 R@5 0.550
* [test_split_families, n=371] MiniLM-L6-v2 (pretrained) | later | R@1 0.499 | R@5 0.755 | MRR 0.613 | lenient R@1 0.604 R@5 0.801

### Paired later-minus-early (bootstrap, 2000 resamples)
* [all_eligible] BM25 mrr: later-early = +0.012 (95% bootstrap CI +0.001..+0.024, n=1193)
* [all_eligible] BM25 recall_at_1: later-early = +0.011 (95% bootstrap CI -0.004..+0.026, n=1193)
* [all_eligible] BM25 recall_at_5: later-early = +0.020 (95% bootstrap CI +0.003..+0.037, n=1193)
* [all_eligible] MiniLM-L6-v2 (pretrained) mrr: later-early = +0.013 (95% bootstrap CI +0.004..+0.021, n=1193)
* [all_eligible] MiniLM-L6-v2 (pretrained) recall_at_1: later-early = +0.014 (95% bootstrap CI +0.003..+0.026, n=1193)
* [all_eligible] MiniLM-L6-v2 (pretrained) recall_at_5: later-early = +0.011 (95% bootstrap CI +0.002..+0.020, n=1193)
* [test_split_families] BM25 mrr: later-early = +0.023 (95% bootstrap CI +0.000..+0.047, n=371)
* [test_split_families] BM25 recall_at_1: later-early = +0.022 (95% bootstrap CI -0.011..+0.051, n=371)
* [test_split_families] BM25 recall_at_5: later-early = +0.038 (95% bootstrap CI +0.008..+0.070, n=371)
* [test_split_families] MiniLM-L6-v2 (pretrained) mrr: later-early = +0.008 (95% bootstrap CI -0.006..+0.022, n=371)
* [test_split_families] MiniLM-L6-v2 (pretrained) recall_at_1: later-early = +0.011 (95% bootstrap CI -0.011..+0.032, n=371)
* [test_split_families] MiniLM-L6-v2 (pretrained) recall_at_5: later-early = +0.005 (95% bootstrap CI -0.008..+0.019, n=371)

## Caveats / failures
* The query is a full question body and the answer is a different post: lexical overlap (BM25) is expected to be strong; a later > early gain may partly be query length, not information.
* Eligible set is selected by an automated filter that may favour threads with verbose askers; selection bias is not quantified.
* Only 1193 queries from a 2x2000-thread pool; no variance across runs/seeds; no FT arm was run (FT-Aware, FT-Random, FT-Full are NOT RUN by design).
* Example rankings:
* thread askubuntu:707394 target askubuntu:a707414: BM25(later) top-3 = ['askubuntu:a703271', 'serverfault:a367327', 'askubuntu:a1468858']
* thread askubuntu:1438422 target askubuntu:a1438603: BM25(later) top-3 = ['askubuntu:a1438603', 'askubuntu:a1229236', 'askubuntu:a888293']
* thread askubuntu:987102 target askubuntu:a987144: BM25(later) top-3 = ['askubuntu:a813028', 'askubuntu:a687796', 'askubuntu:a472707']
* Reproduce: `python -I pilot/stackexchange_raw/scripts/04_retrieval_smoke.py`
