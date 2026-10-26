# EvidenceRun - Work Plan

Course project for "Building Conversational AI Systems with LLMs and Agents" (HIT, Dr. Alexander Apartsin). Authors: Liza and Shai.

This plan is grounded in:
- The lecturer's refined project direction and dataset creation recipe (shared with the team on 2026-10-26)
- The course syllabus, milestone guides, and course bots on the course site
- The team's earlier design work on the project idea (October 2026)

Repository: https://github.com/shaico111/evidencerun

## 1. Project summary

EvidenceRun investigates symptom-aware retrieval for technical support: matching a user's incomplete natural-language problem description to the right solution (runbook). The working hypothesis, proposed by the course lecturer and to be tested in this project, is that a retrieval model trained to account for frequently missing symptoms may outperform models trained on complete case descriptions.

Full problem statement, hypothesis, and experimental design: see README.md.

## 2. Course milestones and requirements (from the course syllabus and guides)

| Milestone | Course week | Weight | Key requirements |
| --- | --- | --- | --- |
| Project proposal presentation | Week 5 | Feedback only | Use case, problem statement, novelty, data/models/evaluation plan, realistic plan |
| Midterm presentation | Week 9 | 20% | Refined definition, review of at least 3 relevant papers (comparison table), dataset obtained/created, EDA, working baseline, initial measurable results, risks, completion plan |
| Final presentation | Week 13 | 40% | Complete technical argument: achievements with evidence, reproducible methodology, results, conclusions; must include at least one trained or fine-tuned model |
| Final GitHub submission | Internal readiness: 2027-01-17; official cutoff to confirm (see dated schedule below) | 40% | Structured repo: README, slides/, src/, notebooks/, data/ (samples + access instructions), results/, requirements, reproducibility |

Presentation dates are provisional mappings of approximate course weeks, not lecturer-confirmed bookings. See the dated schedule below.

Course policy: AI tools are encouraged for code and slides, provided the project demonstrates novelty and the team keeps full ownership of all submitted material.

Course bots exist for each milestone (Project Advisor, Proposal Reviewer, Midterm Report Reviewer, Final Presentation Reviewer, Repository Submission Validator). They are ChatGPT GPTs linked from the course bots page. They have been identified but not yet run; the phase plan includes a review pass with the matching bot at each milestone.

Relevant course reading (from the syllabus week topics, course textbook "Building Language AI: From Tokens to Agents"): synthetic data generation and LLM judges (Ch. 15, 42, 46), embeddings and retrieval-augmented generation including DPR (Ch. 31, 32, 35), fine-tuning and PEFT (Ch. 16, 17).

## 2A. Dated schedule and finish line

Updated 2026-10-26. All dates use Asia/Jerusalem. Internal targets below are a proposed work schedule, not official course deadlines, assignments of responsibility, or claims that work is complete.

### Verified anchors and provisional dates

- HIT's official regular Semester A 5787 calendar starts **Sunday, 2026-10-18** and ends **Sunday, 2027-01-17**. Exams begin 2027-01-18. Source: https://www.hit.ac.il/students/calender/
- This course meets on Mondays. Counting the first course week from Monday, 2026-10-19 gives the provisional presentation dates below. The semester's listed Oct27 and Dec6 non-teaching days do not fall on this course's Monday meetings. Rescheduling by the lecturer can still change the mappings.
- Sasha's course timeline in slides 1022/1023 is proposal in week 5, interim in week 9 (generated data, EDA, baseline), and complete-project presentation in week 13. The work schedule below follows that order. His shared project proposal and dataset recipe supply the technical sequence, not a separate dated schedule.
- The current Moodle announcements forum was empty when checked on 2026-10-26; no dated presentation/submission announcement was available there. The linked student-portal syllabus was unavailable. These provisional dates must not be presented as confirmed class appointments.

| Course checkpoint | Provisional course date | Internal ready-by target |
| --- | --- | --- |
| Week 5 proposal | Monday, 2026-11-16 | Thursday, 2026-11-12 |
| Week 9 interim: generated data + EDA + baseline | Monday, 2026-12-14 | Thursday, 2026-12-10 |
| Week 13 complete-project presentation | Monday, 2027-01-11 | Thursday, 2027-01-07 |
| Ready-to-submit repository | Semester end: Sunday, 2027-01-17 | Sunday, 2027-01-17 |

### No routine work after semester end

The project goal is a submission-ready repository by **2027-01-17**, including reproducibility, slides, results, README, permitted data artifacts and the repository-validator review. Core implementation and analysis finish before the final presentation, leaving Jan8-17 for final packaging, feedback and a clean-environment run.

**2027-01-18 through 2027-01-31 is reserved solely for unexpected fixes, not planned development.** This is the requested two-week contingency window after semester end, not a verified official submission deadline. Slide 1023 says semester end + two weeks, while slide 1022 says two weeks after the last class (the Monday mapping would be Jan25); the public syllabus says course end. Confirm the actual official cutoff before relying on any post-semester grace. The Jan17 internal finish line is earlier than all of these two-week interpretations.

### Critical path and dated outputs

| Work block | Internal target | Required output |
| --- | --- | --- |
| Dataset choice and feasibility | 2026-11-01 | Dataset comparison, rights/privacy checks, extraction feasibility (#1) |
| Extraction and inventory | 2026-11-08 | Reproducible case-solution pairs, inventory and initial EDA (#2-3) |
| Proposal ready | 2026-11-12 | Evidence-based proposal deck, review and rehearsal (#15) |
| Symptoms, annotation pilot, frozen splits | 2026-11-22 | Symptom extraction, label guidelines, reviewed pilot/cost estimate, split manifest (#4-5, #7) |
| Annotation validation | 2026-11-29 | Multi-model agreement and reviewed disagreements (#6) |
| Generation, QC, independent evaluation, baseline | 2026-12-06 | Generated data + quality report + held-out set + baseline numbers (#8-11) |
| Interim ready | 2026-12-10 | Paper comparison table, EDA, baseline and risk/completion plan (#16) |
| DPR-Full | 2026-12-20 | Logged fine-tuned complete-description model (#12) |
| DPR-Partial | 2026-12-27 | Matched-budget missing-symptom model (#13) |
| Analysis complete | 2027-01-03 | Stage/observability results, error analysis, limitations (#14) |
| Final talk ready | 2027-01-07 | Complete results-based deck, review and rehearsal (#17) |
| Submission-ready release | 2027-01-17 | Reproducible repository with all required artifacts (#18) |

Every issue has its own planned start, internal target and dependencies; [TASKS.md](TASKS.md) is the full dated index. Frozen case/solution splits precede all synthetic generation. Independent evaluation and baseline work run alongside training-data generation after split/annotation prerequisites. Generation cost estimates are planning outputs, not spending approval.

### If the plan slips

Check progress at each target. Protect a valid controlled comparison and the Jan17 finish line: narrow dataset size or use the smaller matched bi-encoder fallback before adding an optional BM25 baseline or extra model family. Keep at least three-paper literature coverage, data-quality checks, equal-budget comparison, human-reviewed evaluation and reproducibility. A required course-scope change must be confirmed rather than silently dropped. Do not assume Liza has agreed to dates or assign anyone without agreement.

## 3. Phase plan

### Phase 0 - Proposal preparation
- [x] Update project definition per lecturer feedback (README revised, 2026-10-26)
- [ ] Build the proposal presentation per the Project Proposal guide (use case with evidence, formal problem statement, novelty, data + models + evaluation plan, realistic plan)
- [ ] Iterate on the proposal with the Proposal Reviewer bot
- [ ] Prepare the in-class proposal talk

### Phase 1 - Dataset selection and inventory
- [ ] Evaluate the lecturer's candidate datasets for case-solution pair extractability: IBM TechQA, Microsoft MSDialog, Stack Exchange (Super User / Server Fault / Ask Ubuntu), Tobi-Bueck Customer Support Tickets, iFixit Troubleshooting (all tentative)
- [ ] Check licenses, redistribution terms, and personal data; publish only permitted, anonymized samples
- [ ] Select the primary source dataset(s) based on: problem descriptions linked to solutions, size, license, cleaning effort
- [ ] Produce a data inventory: counts, fields, examples, known gaps
- [ ] Exploratory data analysis (feeds the midterm)

### Phase 2 - Case and symptom annotation
- [ ] Extract cases (problem description + linked solution) from the chosen dataset
- [ ] LLM-based symptom extraction per case (consolidated symptom list)
- [ ] Write annotation guidelines, examples, uncertainty/abstention rules; pilot on a small reviewed sample and estimate generation cost before a full run
- [ ] LLM-based annotation of each symptom: Stage (early / intermediate / advanced) and Observability (high / medium / low)
- [ ] Multi-LLM independent validation of annotations; flag and review disagreements; measure agreement (including a chance-corrected metric where appropriate); do not treat inferred symptoms as confirmed observations
- [ ] Freeze train / validation / test splits BEFORE any synthetic generation; group duplicate cases and related solution documents so near-identical content cannot leak across splits. Record whether evaluation tests unseen cases or unseen solutions

### Phase 3 - Synthetic description generation
- [ ] For each case, generate three natural-language descriptions (early / intermediate / advanced stage), sampling symptoms by stage and observability
- [ ] Pilot structured JSON records with schema validation (e.g., Pydantic); choose a simple generation runner, with DataDreamer/Curator as course-covered options and LangGraph optional for retries and validation
- [ ] Quality control gates: only eligible symptoms, technical consistency, original solution remains valid; record rejection reasons
- [ ] Generate the evaluation set independently (different prompt/template, ideally a different model) to reduce generator-style leakage; manually screen it
- [ ] Small human-written or human-edited test subset to check that trends hold beyond synthetic text

### Phase 4 - Models and training
- [ ] Baseline: off-the-shelf embedding models (no fine-tuning); keep candidate corpus, representations, and evaluation queries fixed across comparisons
- [ ] Specify DPR dual-encoder contrastive objective, positive pairs, and negative sampling; check negatives for false negatives when several solutions are valid
- [ ] DPR-Full: DPR fine-tuned on complete case descriptions
- [ ] DPR-Partial: DPR fine-tuned on synthetic descriptions with missing symptoms
- [ ] Keep encoder, data size, and training budget equal between DPR-Full and DPR-Partial so only the data generation method differs

### Phase 5 - Evaluation and analysis
- [ ] Primary metrics: Recall@K and MRR, reported across symptom stages and observability levels. Fix K and relevance labels before comparison; distinguish source-solution hit rate from full relevance recall when only one known solution is labeled
- [ ] Calibrate criterion-specific LLM judges against a human-reviewed sample; do not treat judge scores as objective ground truth
- [ ] Synthetic data quality metrics: leakage checks, duplicate rate, grounding/validity, annotation agreement
- [ ] Error analysis: where DPR-Partial helps or hurts vs DPR-Full
- [ ] Optional secondary baseline: BM25 (lexical), from earlier design work

### Phase 6 - Milestone deliverables
- [ ] Midterm presentation (Phase 1-4 results, paper comparison table, baseline numbers) + Midterm Report Reviewer bot pass
- [ ] Final presentation per the Final Presentation guide + Final Presentation Reviewer bot pass
- [ ] Repository completion per the GitHub Submission guide (structure, README, slides in editable PPTX and PDF, data samples, visuals, machine-readable result logs, reproducibility) + Repository Submission Validator bot pass

## 4. Methodological guardrails (carried from the team's design history)

- Split data before generation, never after: leakage between train and test versions of the same case invalidates the comparison.
- Evaluation descriptions come from an independent generation process; otherwise results may measure generator style rather than generalization.
- Annotation adherence is measured and reported, but is not used as an acceptance gate for one arm only; filtering must be identical across arms.
- Keep every generated record's metadata: source case, stage, sampled symptoms, generation config, QC results, rejection code.
- Report negative and ambiguous results honestly; scope changes are expected and explained at each milestone.

## 5. Open questions

- Course comparison scope: lecturer feedback proposes DPR-Full vs DPR-Partial plus off-the-shelf baselines. General slides ask for several fine-tuned and off-the-shelf models; document the proposed controlled comparison and confirm whether another encoder family is expected before expanding scope.
- Primary source dataset: to be decided in Phase 1 from the candidate list (a proposal, not a settled choice).
- Annotation reliability: whether LLM stage/observability labels reach usable agreement; fallback is narrowing the annotation scheme.
- Compute budget for DPR fine-tuning; fallback is a smaller bi-encoder (e.g., SentenceTransformer) with the same experimental design.

## 6. Sources

Course-linked materials:
- Official HIT 5787 academic calendar: https://www.hit.ac.il/students/calender/
- Current course announcements (login required): https://md.hit.ac.il/mod/forum/view.php?id=972024
- Actual HIT Moodle course (login required): https://md.hit.ac.il/course/view.php?id=27808
- Lecture slide library linked by Moodle: https://drive.google.com/drive/folders/1-l4pdsXg-nfKQs0t5ZkxjIjOwhwkmv_Z?usp=sharing
- Reviewed relevant lecture PDFs: 1022 Course Structure; 1023 Project Requirements; 1041 Student Reviews example; 1042 Project Examples; 1221 Synthetic Data; 1222 Labeling; 1223 Weak Supervision; 1224 Anonymization; 1241 Text Metrics; 1242 LLM Judges; 1321 PEFT; 1323 Representation Fine-Tuning; 1401 Vector Stores; 1402 RAG Intro; 1403 RAG Evaluation; 1404 Advanced RAG. Slides are referenced, not copied into this repository.

Public course materials:
- Course syllabus: https://www.apartsin.com/teaching/large-language-model-nlp-undergraduate-syllabus.html
- Course textbook (open access): https://llmbook.icsgen-ai.org/
- Milestone guides: https://www.apartsin.com/teaching/guides/project-proposal-presentation.html , https://www.apartsin.com/teaching/guides/midterm-presentation.html , https://www.apartsin.com/teaching/guides/final-presentation.html , https://www.apartsin.com/teaching/guides/github-submission.html
- Course bots: https://www.apartsin.com/teaching/course-bots.html
- Past student projects: https://www.apartsin.com/teaching/hands-on-ai-science-courses-student-projects.html

Team project inputs (shared as links, not republished here): the lecturer's refined proposal and dataset creation recipe shared with the team on 2026-10-26; the team's project design history from October 2026.
