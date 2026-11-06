# Stage 10 Evaluation Report

## Executive summary

The final mock-mode automated suite passed 134 tests with three test-discovered defects fixed:
outdated approval reports now block export, JavaScript URL normalization is safer, and prompt
injection detection covers additional instruction patterns. The browser flow was manually exercised
in mock mode; scripted browser E2E, live-provider measurement, and human evaluation remain pending.

## Scope and provider

All executed automated results came from mock mode unless explicitly identified otherwise.

## Results

| Level | Result |
|---|---|
| Unit/API/reliability/security | 134 tests collected and passing |
| Browser walkthrough | Mock UI flow manually exercised; screenshots saved; no scripted E2E suite |
| Stage 9 smoke exports | JSON, DOCX, and PDF created successfully |
| Human evaluation | Pending; no ratings fabricated |
| Live provider | Not executed without credentials |

## Coverage

Whole-project line coverage: **87%** across 2,421 statements (2,116 covered). The project-wide
85% line-coverage threshold was met. Export service coverage: **90%**; package assembler: **95%**.

## Security findings

No known critical Stage 10 security finding remains. XSS handling for `javascript:` URLs, outdated
export approval gating, false quality-check findings on structural metadata, and injection-detection
coverage were improved during testing.

## Content metrics

The mock metrics ran 40 product/persona combinations across four products and ten personas.
Observed mock results: social length compliance 100%, numerical fact fidelity 25%, schema validity
after generation 100%, forbidden-word compliance 100%, and mean persona Jaccard similarity 1.0.
The identical mock copy across personas and low fact fidelity on three test products show why mock
metrics do not estimate live-model quality. Full output: `content_metrics_mock.json`.

## Performance and cost

No vendor-backed performance or cost claim is recorded. Vendor pricing was not configured and no
live model calls were made.

## Defects

Three defects were fixed; see [defect log](04_defect_log.md). The measured mock metric failures are
not represented as fixed.

## Known limitations

Keyword rules miss paraphrases; word lists and slogan lists are small; LLM judges can be wrong;
mock mode does not measure real model quality; and testing does not replace human or legal review.
The system does not guarantee factual accuracy, legal compliance, or real-world ad performance.
