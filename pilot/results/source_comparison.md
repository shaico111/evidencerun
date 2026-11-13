# Source comparison (automated-proxy pilot, seed 42, n=100/source)

**Read this first.** Human annotation (relationship grades, "material new fact", double-annotation of 60 cases, kappa, minutes/case, leakage and multi-target audits) has **not** been done. Everything below comes from `scripts/04_analyze.py`, which computes objective proxies. Where possible the proxies were built to be *upper bounds* for protocol viability, so low numbers are informative and high numbers are provisional. The protocol's formal PROMISING / CONDITIONAL / NOT SUITABLE verdicts therefore remain **PENDING** except where an upper bound already falls below a gate.

## Funnel (counts out of 100 sampled; frame sizes are full eligible frames)

| Stage | GitLab (N=5,002) | Wikimedia (N=613) | MANtIS, 5 domains (N=43,043) |
|---|---:|---:|---:|
| Fetched | 100 | 100 | 100 |
| Troubleshooting (proxy) | 96 | 95 | 55 |
| >=3 stages, grade >=1 (proxy) | 72 | 50 | 21 |
| 3 stages, grade 2 "observed" (proxy) | 72 | 0 | 21 |
| Accessible explicit target (proxy) | 6 | 10 | 18* |
| **Tier A upper-bound proxy** | **6** (Wilson 2.8-12.5%) | **3** (1.0-8.5%) | **11** (6.3-18.6%, links unverified) |
| Tier B proxy | 6 | 3 | 18* (11.7-26.7%) |
| Unique Tier A proxy targets | 7 | 1 | 17 |

*MANtIS release deviation: every `is_answer` flag in this JSON is `'0'` (checked on all 62,319 dev utterances), so **no accepted-answer labels exist**. Tier B uses the top-voted answer post (votes >= 1) as a substitute. This is a recorded deviation, not the protocol's "accepted answer".

Full metrics with CIs: `metrics.csv`. Funnel: `funnel.csv`. Per-case proxy flags: `../annotations/auto_proxy_cases.jsonl`.

## What the numbers say

- **GitLab**: best chronology (timestamped human notes; proxy 72%). Incident-to-runbook mapping is the weak side: only 6/100 incidents link a runbooks page at all, and the URLs show most are **config/metric-catalog files** (`*.jsonnet`, `rules/*.yml`), not troubleshooting procedures. Real Tier A yield is plausibly 1-3/100. Below the 10/100 gate even as an upper bound -> **NOT SUITABLE as primary Tier A** (caveat: the link regex covers only runbooks.gitlab.com and the gitlab-com/runbooks repo).
- **Wikimedia**: no contemporaneous messages, so chronology is at best grade 1 (retrospective timeline, 50 proxy). Only 3 cases link a keyword-matching operational page, all to the same page (`MariaDB/troubleshooting`): 1 unique target. Upper bound below gate -> **NOT SUITABLE as primary Tier A** (caveat: target detection is title-keyword based and may miss some). The small frame (613) also caps scale far below 500+ viable cases.
- **MANtIS**: weakest chronology yield (21% have >=3 substantive seeker turns) and no document-ranking labels in this release, but the only source with target diversity (17 unique among 11 pairs). The 11 Tier A candidates are reachable external URLs from answers; whether they are real troubleshooting guides and relevant is **unverified**, and a substantial drop is expected. Tier B (18% under the votes substitute) sits in the CONDITIONAL band and would redefine the task from runbook retrieval to answer retrieval.
- MANtIS by domain (sampled / stage-3 proxy / Tier B proxy): askubuntu 41/12/10, electronics 25/2/2, apple 13/2/2, dba 12/3/2, security 9/2/2. Askubuntu carries the yield.

## Provisional reading (not a final decision)

| Item | Provisional |
|---|---|
| Original Tier A with runbooks | No source clears the gate on automated evidence. GitLab and Wikimedia fail even on upper bounds. MANtIS is unverified. |
| Best chronology source | GitLab (timestamped, observed) |
| Best document-mapping source | MANtIS (Tier B, revised task; targets are answer texts) |
| Decision | **CONDITIONAL / NO-GO for strict Tier A.** A mixed design (MANtIS for training, GitLab as a small chronology eval) is the protocol's own fallback; it needs a human check first. |

## What must be verified next

1. Human-annotate the MANtIS stage-3 (21) and Tier A (11) candidates (are links real guides? are follow-up turns new facts?), then the 6 GitLab and 3 Wikimedia candidates.
2. Double-annotate 20 per source and compute kappa.
3. Check whether another MANtIS mirror or the original Stack Exchange dumps carry accepted-answer flags.
4. Measure leakage, multiple-valid-target rate, truncation and annotation minutes; none were measured here.
5. Confirm licensing for each source before any redistribution.
