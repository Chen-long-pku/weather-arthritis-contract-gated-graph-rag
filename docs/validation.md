# Validation and data-sharing notes

This code-only repository contains scripts and documentation needed to inspect the software methods. It does not include raw clinician-review workbooks, question-level adjudication datasets, or internal quality-control logs.

The manuscript reports clinician-adjudicated answer-level outcomes using tables and figures submitted with the article and Supplementary Materials. De-identified question-level and clinician-rating data can be requested from the corresponding author, subject to author approval and journal policy.

## Reproducibility boundary

The scripts can reproduce preprocessing and analysis logic when the locked study inputs are supplied. Public release of code does not imply public release of every source workbook used during blinded review.

## Extraction quality-control boundary

The quote-first extraction workflow generates expert-auditable graph candidates by requiring exact evidence-span anchoring. Candidate relations should not be described as curated graph edges until human review has been completed.
