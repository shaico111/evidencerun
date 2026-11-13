# EvidenceRun — Measurable Dataset Feasibility Pilot

**Candidate sources:** GitLab Production Incidents + Runbooks, Wikimedia Incident Reports + Operational Documentation, and MANtIS.

**Purpose:** Choose a defensible primary dataset for researching whether training a retriever on *stage-aware, partially observed problem descriptions* improves retrieval of the correct troubleshooting document.

**Status:** Execution protocol, not results. All thresholds below are proposed decision rules; they are **not** claims about any dataset. Record deviations before inspecting outcomes.

---

## 1. The decision this pilot must answer

We need a source that supports **all three** of these requirements:

1. **Real cases:** independently observed troubleshooting incidents or dialogues, not fabricated examples.
2. **Information progression:** evidence becomes available in at least three **chronologically defensible** snapshots: Early, Intermediate, and Advanced. The snapshots must contain cumulative, materially new observations from the *same* case.
3. **Retrievable target:** an accessible, independent troubleshooting document that can be validated as relevant to the case. A merely similar document or the case's own postmortem is not sufficient.

**Do not conflate two different tasks:**

- **Tier A — Strict Runbook Retrieval:** retrieve an existing operational runbook / troubleshooting guide from a separate document corpus. This most closely preserves the original EvidenceRun proposal.
- **Tier B — General Solution Document Retrieval:** retrieve an accepted answer, knowledge-base article, external technical guide, or other independently accessible solution text. This can support a revised research question, but is **not** automatically equivalent to Tier A.

Evaluate and report the two tiers separately. A source that is good for Tier B but weak for Tier A must not be described as a proven runbook dataset.

### Key source entry points

| Source | Case collection | Candidate solution documents |
|---|---|---|
| GitLab | [Production issue tracker](https://gitlab.com/gitlab-com/gl-infra/production/-/issues), including incident reviews and explicit incident records | [GitLab Production Runbooks](https://runbooks.gitlab.com/) |
| Wikimedia | [Wikitech incident documentation](https://wikitech.wikimedia.org/wiki/Category:Incident_documentation) and linked incident timelines | Wikitech runbooks, operational guides, and explicitly cited troubleshooting documentation |
| MANtIS | [MANtIS project](https://guzpenha.github.io/MANtIS/), [code / dataset information](https://github.com/Guzpenha/MANtIS), and any independently verified mirror | Document-ranking targets, linked external documents, and (for Tier B only) qualifying answer texts |

**Access caveat:** Dataset mirrors and source pages may omit fields, have broken links, or impose different licensing terms. Verify the actual files and terms. Do not assume a dataset card guarantees document-ranking labels or full conversation history.

---

## 2. Pilot size and sampling (pre-register before annotation)

### Required sample

- Sample **100 raw cases per source**: **300 cases total**.
- Use `random_seed = 42` for reproducible sampling.
- Save the **entire sampling frame**, sampling procedure, timestamps, and selected IDs before inspecting individual cases.
- Do **not** intentionally select only long, rich, already-solved, or runbook-linked cases. We need the *yield from the natural source*, including failures.
- If a record is unavailable or ineligible, keep it in the denominator and record why. Do **not** silently replace it.
- Independently double-annotate **at least 20 cases per source** (60 total), sampled from the 100. Resolve disagreements after recording initial labels.

### Source-specific frames

**GitLab:** Identify the public set of actual production incident issues/reviews using a documented label, issue type, incident index, or other reproducible rule. Do not sample all GitLab issues as if they were incidents. Save exact API filters/URLs. Exclude unrelated engineering tasks *after* sampling and report their count if the sampling frame could not exclude them reliably.

**Wikimedia:** Form a reproducible inventory of distinct incident reports (not category pages, process templates, navigational pages, or duplicate transclusions). If using an incident category, record the rule used to identify genuine incident pages. Sample uniformly from that inventory.

**MANtIS:** Form a reproducible subset of technical-support domains (e.g., Ask Ubuntu, Apple, Database Administrators, Security, Electronics). Record domain counts. Sample **proportionally across the chosen domains**, rather than manually picking examples with visible links. Report results by domain as well as overall. Ensure that the downloaded version preserves turn order, speakers, and any available timestamps and target-document metadata.

### Record the actual denominators

For each source, report:

`sampling_frame_size -> sampled_raw (100) -> fetched -> genuine_troubleshooting -> >=3_valid_stages -> verified_target -> Tier_A_viable / Tier_B_viable`

These are nested counts, except Tier A and Tier B should also be shown separately and may overlap. Report losses and reasons at each stage.

---

## 3. Common annotation rubric (identical for all sources)

### A. Is this a real troubleshooting case?

- `case_valid = 1`: a specific technical problem, failure, degradation, configuration issue, or incident requiring diagnosis or remediation.
- `case_valid = 0`: general discussion, conceptual Q&A, feature request, announcement, routine maintenance, or insufficient evidence of a problem.

### B. Are there three genuine information stages?

A **stage** is a snapshot of information actually known/recorded at a point in the investigation, not an arbitrary paraphrase with fewer words.

- **Early:** initial symptoms/impact available before diagnosis.
- **Intermediate:** initial information **plus** a distinct diagnostic observation documented later.
- **Advanced:** the first two snapshots **plus** another distinct observation documented before the final resolution. If the answer/root cause is already stated verbatim, flag it as a possible retrieval shortcut.

Use **cumulative** snapshots: `Early ⊆ Intermediate ⊆ Advanced` in factual content. Each transition must add at least one *material*, case-specific fact (not thanks, repeated wording, suggestions untested by the user, or unrelated commentary).

Store both the snapshot text and supporting **verbatim evidence spans**, source URLs, and message/event timestamps if available.

**Chronology confidence** (`chronology_grade`):

- `2 = observed`: original, time-ordered messages/logs establish when the new observation was reported.
- `1 = reconstructed`: a retrospective report explicitly dates the observations; evidence is plausible but we do not have the contemporaneous messages.
- `0 = unsupported`: the ordering is inferred, hypothetical, or invented.

**Primary stage-viability criterion:** at least three cumulative snapshots and `chronology_grade >= 1`, with no fabricated observations. Report grade 2 separately; it is the stronger evidence.

**Critical rule:** A diagnostic *instruction* ("check Redis latency") is not a finding ("Redis latency increased"). A list of possible causes is not proof that those causes occurred in a given case.

### C. Stage and observability annotations

For **each newly revealed observation**, label:

- `stage_first_known`: `early | intermediate | advanced` based on the documented record; do not guess its real-world onset.
- `observability`: `high` (normally visible from user-facing symptoms or standard alerts), `medium` (requires basic technical inspection), or `low` (requires logs, traces, specialist tooling, or deep investigation).
- `observability_basis`: one sentence justifying the label.

**Distinguish** when a symptom *happened* from when it was *known*. An issue can start early but only become observable later. Record both times if available.

### D. Target-document evidence and quality

A target must be **separate from the case description**. Do not use the incident postmortem itself as the document to be retrieved, since it contains the answer and creates label leakage.

For every proposed target, record:

- `target_type`: `operational_runbook | troubleshooting_guide | knowledge_base | external_technical_doc | accepted_answer | other`
- `target_url`, `target_id`, `target_title`, whether its **full text is accessible**, and a content hash if stored.
- `relationship_grade`:
  - `3 = confirmed`: the source explicitly documents use of this document/procedure in a successful resolution, or another comparably strong, verifiable resolution link.
  - `2 = explicit_relevant`: the case/answer directly references or recommends the document for the problem, but successful resolution is not demonstrated.
  - `1 = inferred_only`: a researcher/LLM considers it semantically related; no explicit evidentiary link.
  - `0 = unsupported_or_wrong`: irrelevant, inaccessible as a document, or contradicted.
- `solution_status`: `confirmed_resolved | recommended_only | unresolved | unknown`.
- `doc_existed_at_case_time`: `yes | no | unknown` (when date evidence exists).

**Primary positive-label rule:** `relationship_grade >= 2` plus independently available text. Report grade 3 counts as a stricter subset. `relationship_grade = 1` is **not** a gold label.

**Tier A:** the target must also be a genuine operational runbook or reusable troubleshooting guide; an accepted forum answer alone does **not** qualify.

**Tier B:** an accepted answer or external knowledge article can qualify if the text actually addresses the case. "Accepted" by itself is *not* proof that an outbound URL is the correct target.

### E. Contamination, ambiguity, and duplication

Record flags for:

- `answer_leakage`: early/intermediate query quotes the document title, link, final fix, or unique diagnosis not yet available.
- `target_is_case_postmortem`: exclude as a retrievable target.
- `multiple_plausible_targets`: several documents legitimately solve the partial query (important for Recall@k interpretation).
- `duplicate_or_near_duplicate_case` and `duplicate_or_near_duplicate_target`.
- `stale_or_missing_document` and `rights_unclear`.

Keep the original evidence. LLM rewriting may improve phrasing **only after** the factual prefixes are frozen, and must not add or move information between stages.

---

## 4. Source-specific checks

### 4.1 GitLab

For each sampled production incident:

1. Capture title, report body, discussion, incident updates, review/postmortem, timestamps, and explicit documentation links.
2. Reconstruct Early/Intermediate/Advanced from **observations** in chronological order. Distinguish live updates from later retrospective analysis.
3. Search the incident and linked follow-up issues for direct runbook references; fetch any linked GitLab runbook page.
4. Verify whether the runbook explains a diagnostic/remediation procedure relevant to the incident, and whether its use is documented or merely inferred.
5. Record if the apparent "runbook match" was added only **after** the incident (possible retrospective bias).

**Failure mode to quantify:** many detailed real incidents but no proven incident-to-runbook mapping.

### 4.2 Wikimedia

For each sampled incident report:

1. Extract reported impact, timeline, investigation steps, decisions, and remediation actions.
2. Distinguish explicit event-time observations from retrospective explanations of root cause.
3. Collect links to runbooks/operational procedures; verify those pages independently.
4. Mark when the report explicitly says **no runbook existed** or the team did **not** use a runbook. Do not force a match.
5. Keep a separate count of cases excellent for **chronological evaluation** but ineligible for Tier A retrieval.

**Failure mode to quantify:** strong, well-timestamped incident sequences but too few reusable document targets.

### 4.3 MANtIS

For each sampled technical conversation:

1. Preserve all available turns in original order, with speaker roles and timestamps where present.
2. Check whether the discussion describes a *particular failure* rather than general informational advice.
3. Identify two or more **new facts contributed by the person reporting the problem**, or by a diagnostic exchange with confirmed results. Assistant suggestions alone do not count as observed facts.
4. Locate the answer and every referenced document; verify whether links are real solutions, background citations, or unrelated resources.
5. Explicitly distinguish an **accepted/answer text** target (Tier B) from an independent **external troubleshooting guide/runbook** (Tier A).
6. Confirm which document-ranking labels are actually present in the obtained dataset version; do not assume that all mirrors contain them.

**Failure mode to quantify:** many long dialogues and hyperlinks, but few verified solution documents or genuinely incremental troubleshooting facts.

---

## 5. Required data files and schemas

Use CSV for summary tables and JSONL for nested text/evidence. Keep raw content separate and do not republish source text unless permitted.

```text
pilot/
  README.md
  config.json
  sampling_frames/
    gitlab_frame.csv
    wikimedia_frame.csv
    mantis_frame.csv
  samples/
    gitlab_sample.csv
    wikimedia_sample.csv
    mantis_sample.csv
  annotations/
    cases.jsonl
    second_annotator.jsonl
    adjudications.jsonl
  results/
    funnel.csv
    metrics.csv
    source_comparison.md
    representative_cases.md
    failure_analysis.md
  provenance/
    source_versions.json
    access_and_licenses.md
```

Minimum `cases.jsonl` record:

```json
{
  "source": "gitlab",
  "case_id": "example-placeholder",
  "case_url": "https://example.org/case",
  "case_valid": true,
  "case_date": null,
  "domain": "redis",
  "chronology_grade": 2,
  "snapshots": [
    {"stage": "early", "text": "...", "evidence": [{"quote": "...", "url": "...", "reported_at": "..."}]},
    {"stage": "intermediate", "text": "...", "evidence": [{"quote": "...", "url": "...", "reported_at": "..."}]},
    {"stage": "advanced", "text": "...", "evidence": [{"quote": "...", "url": "...", "reported_at": "..."}]}
  ],
  "observations": [
    {"fact": "...", "stage_first_known": "intermediate", "observability": "medium", "observability_basis": "..."}
  ],
  "target": {
    "target_id": "...",
    "target_url": "...",
    "target_type": "operational_runbook",
    "full_text_accessible": true,
    "relationship_grade": 2,
    "solution_status": "recommended_only",
    "doc_existed_at_case_time": "unknown"
  },
  "tier_a_viable": true,
  "tier_b_viable": true,
  "flags": [],
  "exclusion_reasons": [],
  "annotation_notes": "..."
}
```

The JSON above is **schema illustration only**, not a real sourced example. In actual records, `tier_a_viable` and `tier_b_viable` must be **computed** from rubric fields, not accepted uncritically from a human/LLM label.

---

## 6. Quantitative metrics (compute separately for each source)

**All rates below must show numerator, denominator, percentage, and 95% Wilson confidence interval.** With only 100 samples/source, estimates are approximate; avoid claiming small differences are decisive.

| Metric | Definition | Why it matters |
|---|---|---|
| Fetch success rate | Retrieved complete case / 100 sampled | Access feasibility |
| Troubleshooting rate | Genuine troubleshooting cases / 100 | Source relevance |
| 3-stage rate | Cases with 3 valid stages and chronology grade >=1 / 100 | Main Stage feasibility |
| Observed-chronology rate | Cases with 3 stages and chronology grade =2 / 100 | Strength of real-time evidence |
| Explicit target rate | Cases with accessible target and relationship grade >=2 / 100 | Gold-label reliability |
| **Tier A yield (primary)** | Cases satisfying all Tier A criteria / 100 | Usability for original project |
| **Tier B yield (secondary)** | Cases satisfying all Tier B criteria / 100 | Usability for revised project |
| Confirmed-solution yield | Tier A/B cases with grade=3 / 100 | Gold-label strength |
| Distinct target count | Number of unique qualified target documents | True retrieval corpus diversity |
| Target concentration | Share of eligible cases mapped to top 10 targets | Detect repeated-target inflation |
| Leakage rate | Viable candidates flagged for answer leakage / viable candidates | Threat to validity |
| Ambiguous-target rate | Reviewed viable candidates with multiple genuinely relevant documents / reviewed viable candidates | Need multi-label relevance |
| Annotation agreement | Raw agreement + Cohen's kappa for case-valid, 3-stage-valid, and target-valid | Rubric repeatability |
| Human effort | Median minutes to verify one raw case and one viable pair | Scalability |

Also report **median and distribution** of unique newly added facts from Early→Intermediate and Intermediate→Advanced. Count only meaningful *observations*, not assistant recommendations or paraphrases.

### Sample-size and corpus projections

For each source, record the known/estimated size of its full **eligible sampling frame** `N`, and report the simple projection:

`projected_viable_pairs = N × observed_Tier_A_or_Tier_B_yield`

This projection is a **rough planning estimate**, not proof of the final dataset size; report a range using the confidence interval, and state when the frame size is unknown. Also report **unique-target projections separately**: do not estimate unique documents simply by multiplying case counts.

---

## 7. Quality audit and bias controls

1. **No cherry-picking:** the first 100 cases per source come from the registered random sample. Showcase examples must be explicitly labeled as examples, not representative estimates.
2. **Blind second review:** 20 cases/source independently assessed before adjudication. Report disagreements and refine definitions, but do not retroactively hide disagreement.
3. **Citation requirement:** every stage-defining observation must link to an original turn, timeline entry, or documented event. Unsupported generated text is invalid.
4. **No hindsight leakage:** do not make the initial query from the final diagnosis, known fix, or runbook title. Reconstruct only information available at each point.
5. **No trivial target leakage:** remove direct document links and explicit solution document names from query snapshots, but preserve ordinary technical clues if genuinely observed. Record every transformation.
6. **Multiple valid targets:** for at least **20 viable cases per source, if available**, inspect the supplied target plus up to **three** plausible alternatives. Record whether the gold set should contain multiple documents.
7. **Document length consistency:** record target token counts and whether a MiniLM-style short embedding truncates essential material. Do not change truncation strategy differently across sources without documenting it.
8. **Deduplication and splitting:** identify related incidents, re-opened threads, near-duplicate questions, and shared solutions. All variants of one case must stay in one train/dev/test split. A stricter evaluation should also group by target document to test unseen-document generalization.
9. **Document corpus composition:** when later benchmarking retrieval, create a realistic candidate corpus with nonrelevant and near-relevant documents. A setting with only one possible target is not retrieval.
10. **Rights and privacy:** log access terms, reuse permissions, author/source attribution, and redaction needs. Do not assume GitLab issue comments, Wikitech pages, and external MANtIS links all share one license.

---

## 8. Decision rules (predefined heuristics)

Treat these as **project planning gates**, not statistically established universal standards.

### Primary: keep the original Runbook Retrieval task (Tier A)

Mark a source **PROMISING** if, in the random 100-case pilot:

- At least **20/100** cases are Tier A viable;
- At least **15 unique** valid target runbooks/guides are observed;
- The target text is retrievable for at least **90% of the Tier A cases**;
- Stage evidence is traceable and the double-annotation quality review finds no systematic invented chronology;
- The complete sampling frame is large enough that scaling toward **500+ viable cases and 200+ distinct target documents** is credible (report `unknown` if not verifiable).

Mark **CONDITIONAL** if **10–19/100** are Tier A viable, or if the mappings/stages require substantial manual adjudication.

Mark **NOT SUITABLE AS PRIMARY TIER A SOURCE** if fewer than **10/100** are viable, or if links are systematically inferred rather than documented.

**Important:** passing the 100-case yield check does **not** prove the unique-document scaling target. Corpus diversity must be verified separately before full training.

### Secondary: broaden to Solution Document Retrieval (Tier B)

Apply the same rates to Tier B, and clearly state that the research target has changed if accepted answers or knowledge-base responses replace runbooks.

### If none passes

Do **not** fabricate missing stage observations or treat semantically similar documents as positives. Options:

- Choose the strongest *chronology* source for a small external evaluation set.
- Choose the strongest *document mapping* source for training.
- Explicitly describe the resulting mixed-source design and its domain-shift limitations.
- Consider an alternative dataset or revise the research question before substantial fine-tuning.

---

## 9. Work plan and acceptance checklist

### Phase 1 — Data access and inventory

- [ ] Verify source URLs, schema fields, licensing, and full-text availability.
- [ ] Build source-specific sampling frames, with counts and selection rules.
- [ ] Freeze seed 42 and save random sampled IDs before reviewing text.

### Phase 2 — Extraction and annotation

- [ ] Fetch 100 sampled cases/source; preserve failures and raw provenance.
- [ ] Identify problem validity and reconstruct stage snapshots with evidence.
- [ ] Validate target-document links, relationship grades, target type, and full-text availability.
- [ ] Double-annotate 20/source; record and adjudicate disagreements.

### Phase 3 — Quantification

- [ ] Produce funnel counts, Wilson intervals, duplicate counts, unique-target counts, and annotation effort by source.
- [ ] Audit source-specific failure types and 20 target ambiguities/source where possible.
- [ ] Produce at least 3 strong cases and 3 failure cases per source, with provenance links (where allowed).

### Phase 4 — Decision

- [ ] Compare Tier A separately from Tier B.
- [ ] State whether the data support **observed**, **retrospectively reconstructed**, or **synthetically imagined** progression; only the first two count toward the pilot's stage yield.
- [ ] Recommend one primary source, a backup, and optionally an external test source.
- [ ] State what remains unknown before full-scale data collection.

**Do not train MiniLM in this pilot.** The immediate decision is whether a trustworthy dataset can be built. A small BM25/pretrained-MiniLM smoke test is optional *after* labels pass review, but its score must not override poor source quality.

---

## 10. Report template (fill in actual results)

### 10.1 Sample and quality funnel

| Metric | GitLab | Wikimedia | MANtIS |
|---|---:|---:|---:|
| Total eligible-frame cases (`N`) | TBD | TBD | TBD |
| Random cases sampled | 100 | 100 | 100 |
| Successfully fetched | TBD | TBD | TBD |
| Valid troubleshooting cases | TBD | TBD | TBD |
| Three valid stages (grade >=1) | TBD | TBD | TBD |
| Three observed stages (grade =2) | TBD | TBD | TBD |
| Accessible explicit target (grade >=2) | TBD | TBD | TBD |
| **Tier A viable cases** | TBD | TBD | TBD |
| **Tier B viable cases** | TBD | TBD | TBD |
| Grade-3 confirmed resolutions | TBD | TBD | TBD |
| Unique Tier A target documents | TBD | TBD | TBD |
| Unique Tier B target documents | TBD | TBD | TBD |
| Answer-leakage flags among viable cases | TBD | TBD | TBD |
| Multiple-valid-target flags | TBD | TBD | TBD |
| Median annotation minutes per raw case | TBD | TBD | TBD |
| Primary Tier A verdict | TBD | TBD | TBD |

Include 95% Wilson intervals in the detailed `metrics.csv` even though this summary table shows counts.

### 10.2 Required qualitative findings

For **each** source, provide:

1. **Three real case examples** (links + Early / Intermediate / Advanced evidence + target link + label justification).
2. **Three failure examples** (e.g., no stages, no target, broken links, ambiguous relevance, retrospective leakage).
3. The top **three exclusion reasons**, with counts.
4. Any source-specific technical blocker and its impact on the estimated yield.
5. A statement about licensing and whether the raw source text may be redistributed.

### 10.3 Final recommendation

```text
Recommended primary source:
Recommended Tier A or Tier B task definition:
Observed viable cases / 100:
95% Wilson interval:
Observed unique target documents:
Known full source-frame size:
Projected eligible pairs (with uncertainty and assumptions):
Estimated annotation cost:
Main threat to validity:
Backup source:
Potential external test source:
Decision: GO / CONDITIONAL / NO-GO
What must be verified next:
```

---

## 11. What to send back for review

Send these artifacts, ideally as a ZIP or repository folder:

1. `results/source_comparison.md` and `results/funnel.csv`.
2. `results/metrics.csv` with numerators, denominators, and confidence intervals.
3. `annotations/cases.jsonl` (or a redacted version if redistribution is restricted).
4. `results/representative_cases.md` and `results/failure_analysis.md`.
5. `provenance/source_versions.json`, access/license notes, the random sampling seed, and exact extraction queries.

**The central decision is not "which source has the most text?" It is "which source yields enough distinct, verifiably linked, chronologically defensible case→document pairs for a fair partial-information retrieval experiment?"**
