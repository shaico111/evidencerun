# Course alignment (requirements read from apartsin.com guides on 2026-11-13; point weights and due dates are NOT stated on the pages read)

Sources: proposal / midterm / final / GitHub-submission guides under https://www.apartsin.com/teaching/guides/ (index page also points to a "Project Requirements" and "Assessment Criteria" page that were **not** read — risk: unseen requirements). No course approval of the Stack Exchange pivot exists; do not claim one.

| Course requirement | Planned EvidenceRun component | Evidence produced in this pilot | Remains | Blocker / risk |
|---|---|---|---|---|
| Evidence-based use case, formal input/output | Offline retrospective benchmark: partial problem description → historical solution answer | Real Q&A threads w/ timestamps, reconstructable prefixes (results/timeline_audit.csv) | Use-case evidence from support literature; fix wording "offline retrospective, not a live helpdesk" | Must not imply live availability of later answers |
| Nontrivial novelty grounded in ≥3 papers | Aware vs Random incompleteness | results/novelty_review.md (7 works) | Comparison table; systematic search | Small measured early→later gain weakens the hypothesis |
| Multi-step pipeline, ≥1 trained/fine-tuned model | extraction → state reconstruction → synthetic augmentation → FT retriever → eval | Extraction + reconstruction + audit implemented; **no fine-tuning run** | FT-Full / FT-Random / FT-Aware | Time; matched budget design |
| Synthetic data with fidelity/quality control | LLM paraphrase/compression of source-grounded states | NOT DONE (deliberately, before leakage gate) | Generator seeing only pre-cutoff evidence; QC | Needs human spot-checks |
| Real independent evaluation data, not from training prompts | Source-grounded held-out early/later states, split by answer family | Frozen family split (split_leakage_audit.md); automated provisional queries | ≥100 human-reviewed held-out states | Human review PENDING |
| Baselines + end-to-end + component metrics | BM25, MiniLM, FT arms | BM25 & MiniLM Recall@1/5, MRR (baseline_results.csv); component-level audit rates | FT arms; per-stage/obs breakdown | — |
| Honest scope / schedule | Early/Later primary; 3-state & observability optional | Gates reported with CIs | Update README/WORK_PLAN after decision | Midterm date per WORK_PLAN (~2026-12-10) |
| Data section: source, counts, splits, license, risks | Stack Exchange dumps (Ask Ubuntu, Server Fault) | provenance/sources.json, funnel_*.csv, license uncertainty noted | Legal check | Licence/terms ambiguity for training use |
| GitHub submission: README, reproducibility, no secrets, seeds | pilot/stackexchange_raw/README.md | Commands, seed 42, hashes, tests (19 passing) | Final README, requirements.txt | — |
