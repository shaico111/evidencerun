# Stack Exchange migration audit (KEEP / ADAPT / REPLACE / ARCHIVE)

Branch `poc/stackexchange-raw-validation`, cut from commit `dacb9aa` (tip of the local `poc/dataset-feasibility-pilot`, which was verified to exist, clean except for untracked zip files). Base chosen because it is the only commit containing the earlier pilot's scripts, results and `docs/`. Nothing on the old branch was modified.

Not in the repository (checked with `git ls-files`): no embedding / BM25 / contrastive-training / evaluation code, no `src/`, no `tests/`. Those rows of the default table therefore have nothing to KEEP; they are *to be built* (NEW) and are marked so.

| Path | Purpose | Status | Action | Reason | Depends on |
|---|---|---|---|---|---|
| `README.md` | Project description (runbook-oriented hypothesis) | ADAPT (later) | Add a short pivot note; **not edited in this pilot** (decision pending the GO/NO-GO) | Avoid rewriting the active proposal before the data gate is decided | `results/decision.md` |
| `WORK_PLAN.md`, `TASKS.md` | Plan and dated tasks for issues #1-18 | ADAPT (later) | Update dataset / milestones only after decision | Same | decision |
| `docs/dataset_feasibility_pilot.md` | Protocol of first pilot | ARCHIVE / KEEP | Untouched; historical evidence | Source-selection attempt 1 | - |
| `pilot/README.md`, `pilot/config.json`, `pilot/provenance/*`, `pilot/results/*`, `pilot/samples/*`, `pilot/sampling_frames/*`, `pilot/annotations/auto_proxy_cases.jsonl` | GitLab / Wikimedia / MANtIS pilot (automated-proxy only) | ARCHIVE / KEEP | Read-only; never mixed into new statistics | Proxy results (Tier-A 6/100, 3/100, 11/100) are not validated rates | - |
| `pilot/scripts/common.py` | HTTP helper + Wilson CI | KEEP / ADAPT | Wilson formula re-implemented identically in `se_common.py` (module reads the old pilot's config at import, so importing it would couple the pilots) | Reuse the statistic, not the coupling | - |
| `pilot/scripts/01_build_frames.py` ... `04_analyze.py` | GitLab/Wikimedia/MANtIS fetchers and Prometheus/runbook proxy analysis | REPLACE for new source | Left intact for provenance | Source-specific; not suitable for Stack Exchange XML | - |
| `.gitignore` | Ignore raw data | ADAPT | Added `pilot/stackexchange_raw/raw/` | Raw third-party text must stay out of Git | - |
| `pilot/stackexchange_raw/scripts/se_common.py` | Streaming XML, hashing, CSV, Wilson | NEW | stdlib | - | - |
| `pilot/stackexchange_raw/scripts/temporal.py` | Cutoff + leakage rules (pure functions) | NEW | Unit-tested | Core of the gate | - |
| `pilot/stackexchange_raw/scripts/02..05_*.py` | frame, audit, retrieval, report | NEW | - | - | dumps |
| Old runbook-only labels / examples | Prometheus alert-to-runbook | DO NOT REUSE | Excluded from new ground truth | Different target | - |
| Retrieval stack (BM25 / MiniLM / contrastive fine-tune / metrics) | not present | NEW (smoke-test scale only) | `04_retrieval_smoke.py` | Nothing to reuse | - |

## Summary
Kept: Git history, issue plan, old pilot as read-only archive, the Wilson-CI convention, seed 42. Changed: nothing in existing files except `.gitignore`. Discarded from the active pipeline: GitLab/Wikimedia/MANtIS fetchers and runbook labels. Added: an isolated `pilot/stackexchange_raw/` module.
