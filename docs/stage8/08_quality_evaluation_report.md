# Stage 8 Quality Evaluation Report

## Method

The deterministic mock provider is used for this evaluation. Automated scores are relative indicators, not guarantees of legal or regulatory compliance.

## Results

The fixture contains 60 deliberately labeled cases. Evaluation output from the current rules:

| Check | True positives | False positives | False negatives | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| absolute_claim | 7 | 0 | 0 | 1.00 | 1.00 |
| personal_data | 2 | 1 | 0 | 0.67 | 1.00 |
| prompt_injection_echo | 2 | 0 | 0 | 0.67 | 1.00 |
| restricted_category | 20 | 0 | 1 | 1.00 | 0.95 |
| unsupported_fact | 4 | 0 | 1 | 1.00 | 0.80 |

## Weakest checks

The personal-data fixture needs label-aware matching because an email can be intentional content; the unsupported-number result needs broader numeric-unit normalization.

## Improvements

The rules were consolidated into `quality-rules-v1`, and numeric fact matching was updated to recognize quantities such as `700 ml`. No second rule pass was required after the initial fixture run.

## Known limits

- Keyword rules can miss paraphrased claims.
- The slogan list is intentionally small and incomplete.
- The LLM judges can be wrong.
- Rules, judges, and scores do not replace human, legal, safety, medical, financial, or regulatory review.
