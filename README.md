# EvidenceRun

Diagnostic Evidence-Aware Synthetic Supervision for Runbook Retrieval

Course project for "Building Conversational AI Systems with LLMs and Agents" (HIT, Dr. Alexander Apartsin). Authors: Liza and Shai.

## Motivation and use case

During a production incident, an on-call engineer often gets an alert, a few logs, and a partial description of the symptoms before the root cause is known. The goal is to help the engineer rank the most relevant operational runbooks. Early in an incident, several runbooks may match similar symptoms, and the information that tells them apart may still be missing.

## Research question

Can diagnostic evidence-aware synthetic incident generation improve runbook retrieval under incomplete information, particularly when candidate runbooks share overlapping symptoms?

## Novelty

Synthetic query generation for training retrievers has been explored (InPars, GPL, Promptagator), and runbook retrieval systems such as Sentry ask-runbooks exist. Our contribution is not retrieval or synthetic data generation itself. We test a generation approach that explicitly controls the availability of diagnostic evidence and the signals that distinguish similar runbooks.

We compare three ways of generating synthetic training data:

1. Naive LLM generation
2. Generic attributed generation, with style and noise attributes
3. Diagnostic evidence-aware generation, with control over partial diagnostic information and distinguishing signals

## Data and methods

Main data source: Prometheus Operator Runbooks (about 108 documents in the public catalog, subject to cleaning and suitability checks). We build retrieval cards from these documents and use an LLM to generate labeled incident descriptions.

## Evaluation

- Evaluation on runbooks not seen during training
- Separate analysis of cases with overlapping symptoms and incomplete diagnostic information
- Quality metrics for the synthetic data, leakage checks, and error analysis
- A small human evaluation set for cases where several runbooks may be relevant, to reduce reliance on synthetic evaluation alone

## Scope

The focus is data generation, fine-tuning, and evaluation, not a complete incident response system.

## Status

Idea stage. Proposal sent to the course lecturer for feedback; the research question may be refined.
