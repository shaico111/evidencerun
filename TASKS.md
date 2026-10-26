# EvidenceRun - Dated Tasks

Updated 2026-10-26. Existing issues #1-18 are the source of task status. Dates below are proposed internal targets, not official course deadlines or commitments by an assignee. No assignees have been set. All dates use Asia/Jerusalem.

**Ready to submit: Sunday, 2027-01-17 (official semester end).** The following two weeks are contingency only. See [WORK_PLAN.md](WORK_PLAN.md) for official-date evidence, provisional presentation dates, dependencies and the submission-cutoff caveat.

| Task | Planned start | Internal target | Depends on |
| --- | --- | --- | --- |
| [#1: Evaluate candidate source datasets](https://github.com/shaico111/evidencerun/issues/1) | 2026-10-27 | 2026-11-01 | none |
| [#2: Data inventory and EDA](https://github.com/shaico111/evidencerun/issues/2) | 2026-11-02 | 2026-11-08 | #1 |
| [#3: Case extraction pipeline](https://github.com/shaico111/evidencerun/issues/3) | 2026-11-02 | 2026-11-08 | #1 |
| [#4: Symptom extraction per case](https://github.com/shaico111/evidencerun/issues/4) | 2026-11-09 | 2026-11-15 | #3 |
| [#5: Stage and observability annotation](https://github.com/shaico111/evidencerun/issues/5) | 2026-11-16 | 2026-11-22 | #4 |
| [#6: Annotation validation](https://github.com/shaico111/evidencerun/issues/6) | 2026-11-23 | 2026-11-29 | #5 |
| [#7: Train/validation/test split](https://github.com/shaico111/evidencerun/issues/7) | 2026-11-16 | 2026-11-22 | #3 |
| [#8: Synthetic description generator](https://github.com/shaico111/evidencerun/issues/8) | 2026-11-30 | 2026-12-01 | #6, #7 |
| [#9: Quality control gates](https://github.com/shaico111/evidencerun/issues/9) | 2026-12-02 | 2026-12-06 | #8 |
| [#10: Independent evaluation set](https://github.com/shaico111/evidencerun/issues/10) | 2026-12-02 | 2026-12-06 | #6, #7; independent of training generation |
| [#11: Evaluation harness and off-the-shelf baseline](https://github.com/shaico111/evidencerun/issues/11) | 2026-11-23 | 2026-12-06 | #2, #7; final baseline on #10 |
| [#12: DPR-Full fine-tuning](https://github.com/shaico111/evidencerun/issues/12) | 2026-12-07 | 2026-12-20 | #9, #10, #11 |
| [#13: DPR-Partial fine-tuning](https://github.com/shaico111/evidencerun/issues/13) | 2026-12-21 | 2026-12-27 | #12; matched training budget |
| [#14: Results analysis](https://github.com/shaico111/evidencerun/issues/14) | 2026-12-28 | 2027-01-03 | #12, #13 |
| [#15: Proposal presentation](https://github.com/shaico111/evidencerun/issues/15) | 2026-11-02 | 2026-11-12 | #1; initial data feasibility from #2/#3 |
| [#16: Midterm presentation](https://github.com/shaico111/evidencerun/issues/16) | 2026-12-07 | 2026-12-10 | #2, #9, #10, #11 |
| [#17: Final presentation](https://github.com/shaico111/evidencerun/issues/17) | 2027-01-04 | 2027-01-07 | #14 |
| [#18: Repository submission readiness](https://github.com/shaico111/evidencerun/issues/18) | 2027-01-08 | 2027-01-17 | #14, #17; include final-presentation feedback |

Do not move unfinished routine work into the contingency window. If a target slips, reduce optional scope first and re-plan the remaining critical path.
