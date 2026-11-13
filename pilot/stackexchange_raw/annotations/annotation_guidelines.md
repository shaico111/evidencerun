# Annotation guidelines — Stack Exchange symptom-aware retrieval pilot

Review sheet: `human_review_queue.csv` (200 simple-random rows = `simple_random_audit`, plus a stratified queue; the two must be reported separately). The automated columns are prefilled; **all human columns are blank**. Fill `review_provenance` truthfully: `human` (one person), `double-human` (two independent people), `LLM-assisted`, or `automated`.

Per thread open the URL, then use the **post revision history** (Stack Exchange "edited" link → revisions) and comment timestamps. The **cutoff** is the time of the first answer (or an earlier comment that already gives away the solution). Use only what existed strictly before the cutoff.

| Field | Values | Guidance |
|---|---|---|
| troubleshooting | yes/no/uncertain | Asker has a concrete fault/symptom to fix (not a how-to, opinion, recommendation). |
| accepted_answer_present | yes/no | Green tick present. |
| accepted_answer_relevant | yes/partial/no/uncertain | Does the accepted answer actually resolve the question as asked? |
| solution_self_contained | yes/no/uncertain | Understandable without the question/comments ("see my comment", link-only = no). |
| preanswer_new_fact_count | integer + evidence IDs | Count **new facts about the problem** by the *asker* after the first version and before the cutoff (new error output, new observed behaviour, environment details). Not: thanks, formatting, re-wording, helper suggestions, "that fixed it". |
| valid_information_states | 1 / 2 / 3+ / unknown | 1 + number of distinct new-fact units (a state needs ≥1 independent new fact). |
| stage_evidence | source span + timestamp per state | Revision ID / comment ID and time. |
| observability | high/medium/low/unknown | How easily the stated role (assume: ordinary end-user of that site, no root diagnostics unless stated) could notice the fact. State role and rationale. Not the same as order of writing. |
| leakage | none/suspected/confirmed + cause | Any query-side fact that reveals or was derived from the solution / post-cutoff edit / solution-bearing comment. A diagnosis disclosed by the asker before the cutoff is legitimate. |
| ambiguity_multiple_answers | yes/no/uncertain | Another answer is equally valid. |
| eligibility_verdict | eligible_2 / eligible_3 / exclude / review | eligible_2 needs ≥2 states AND relevant accepted answer AND no confirmed leakage. |
| review_provenance | automated / LLM-assisted / human / double-human | |

Minimum protocol: ≥30 rows per site reviewed by one human; ≥20 per site independently by a second human **without seeing the first label**; report raw agreement and Cohen's kappa (or explain if a class has no variance); reconcile and store the reasons. Do not look at automated columns before labelling if possible (blind first, then compare).
