# Dataset feasibility pilot (POC branch)

Protocol: [`../docs/dataset_feasibility_pilot.md`](../docs/dataset_feasibility_pilot.md). Results: [`results/source_comparison.md`](results/source_comparison.md).

Run order (from `pilot/scripts`, with `PYTHONPATH=.`): `01_build_frames.py`, `02_sample.py`, `03_fetch.py`, `04_analyze.py`. The MANtIS archive must first be extracted into `raw/mantis/extracted/` (see `provenance/`). `raw/` is gitignored.

Done: frames, seeded sampling (seed 42), fetch of all 300 cases, automated proxy funnel with Wilson CIs.
Not done: human annotation, double-annotation, kappa, leakage/ambiguity audits, qualitative examples.
