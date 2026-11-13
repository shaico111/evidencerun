# Stack Exchange raw-data validation pilot (branch `poc/stackexchange-raw-validation`)

Offline, **retrospective** feasibility audit of Ask Ubuntu and Server Fault dumps for Symptom-Aware Solution Retrieval. The accepted answer is a later-written, frozen-corpus target; it was never retrievable by a live helpdesk at query time.

Reproduce (Python 3.12; `pip install py7zr rank_bm25 sentence-transformers`; ~2 GB download, ~10 GB disk):
```bash
# download (Internet Archive item 'stackexchange'; SHA-1 checked in provenance/sources.json)
curl -L -o raw/askubuntu.com.7z  https://archive.org/download/stackexchange/askubuntu.com.7z
curl -L -o raw/serverfault.com.7z https://archive.org/download/stackexchange/serverfault.com.7z
python -I scripts/01_provenance.py
python -I scripts/02_frame_and_fetch.py askubuntu && python -I scripts/02_frame_and_fetch.py serverfault
python -I tests/test_temporal.py
python -I scripts/03_reconstruct_audit.py
python -I scripts/04_retrieval_smoke.py
python -I scripts/05_report.py
```
(`-I` isolated mode; run from `pilot/stackexchange_raw/`, `raw/` is gitignored — raw third-party text is never committed.) Seed 42 in `config.json`.

* `scripts/temporal.py` — the cutoff / leakage rules (pure functions; 20 unit tests in `tests/`).
* `annotations/` — guidelines, blank human review queue (PENDING), LLM-assisted review (clearly labelled, not human).
* `results/decision.md`, `results/report_for_chatgpt.md` — start here.
