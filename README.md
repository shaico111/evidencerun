# EvidenceRun

Symptom-Aware Retrieval for Technical Support

Course project for "Building Conversational AI Systems with LLMs and Agents" (HIT, Dr. Alexander Apartsin). Authors: Liza and Shai.

## Problem

People contact technical support and describe their problems in natural language. Standard retrieval methods (e.g., embedding-based RAG) can match these descriptions to solutions (runbooks), assuming all relevant symptoms are reported. In practice, descriptions are often incomplete for two reasons:

1. Some symptoms appear only at later stages of the problem.
2. Users may overlook or fail to recognize certain symptoms.

## Proposed hypothesis

The project direction, refined with the course lecturer, proposes the following hypothesis, to be tested in this project rather than an established finding:

A retrieval model trained to account for frequently missing symptoms may outperform models trained on complete case descriptions.

## Research question

Does training on realistic, incomplete symptom descriptions improve solution retrieval compared with training on complete symptom descriptions?

## Data

The planned dataset consists of case-solution pairs derived from existing technical support corpora. For each case, the goal is to derive a consolidated symptom list linked to its solution, with each symptom annotated with:

- Stage: early, intermediate, or advanced (when the symptom typically appears)
- Observability: high, medium, or low (how likely a user is to notice and report it)

Candidate source datasets (tentative, under evaluation) include IBM TechQA, Microsoft MSDialog, Stack Exchange (Super User, Server Fault, Ask Ubuntu), Tobi-Bueck Customer Support Tickets, and iFixit Troubleshooting. These corpora do not provide symptom lists, stage or observability annotations, or explicit case-solution links in the required form; deriving and validating them is part of the research.

## Planned dataset creation pipeline

1. Extract cases: problem descriptions and candidate solutions from the chosen source dataset.
2. Split cases into training, validation, and test sets before any synthetic generation, to prevent leakage between versions of the same case.
3. Extract symptoms: use an LLM to build a consolidated symptom list per case.
4. Annotate symptoms: use an LLM to label each symptom with stage and observability.
5. Validate annotations: multiple LLMs independently extract and label; disagreements are flagged for review. Inferred symptoms are not treated as confirmed observations.
6. Generate synthetic descriptions: for each case, three natural-language descriptions at different stages, sampling symptoms by stage and observability.
7. Quality control: generated descriptions must contain only eligible symptoms, stay technically consistent, and keep the original solution valid.

## Planned experimental comparison

1. Baseline: off-the-shelf embedding models.
2. DPR-Full: DPR fine-tuned on complete case descriptions.
3. DPR-Partial: DPR fine-tuned on synthetic descriptions with missing symptoms.

Retrieval accuracy would be evaluated with Recall@K and MRR, analyzed across symptom stages and observability levels.

## Scope

The focus is data generation, fine-tuning, and evaluation, not a complete technical support system.

## Status

Proposed methodology, refined per lecturer feedback (October 2026).
