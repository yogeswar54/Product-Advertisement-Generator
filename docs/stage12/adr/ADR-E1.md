# ADR-E1: Hindi Generation Support

- **Status:** Accepted for Stage 12; implementation is opt-in.
- **Decision scope:** Hindi (`hi`) only. Other regional languages remain deferred.

## Context

Stage 1 defines English as the MVP launch language and lists additional-language support as a
production-level “Could” NFR. The current input schema accepts a language-tag pattern rather than
an enum, and the UI presents a free-text language field. Generation prompts and audience
vocabulary are English-oriented. English keyword/readability checks do not apply reliably to
Devanagari, and the PDF exporter currently draws text using Helvetica. The mock content metrics do
not measure Hindi quality.

## Options

1. Keep English-only behavior and defer all language work.
2. Add Hindi output with language-aware prompts, audience vocabulary guidance, explicit quality
   check applicability, and a documented PDF-font limitation.
3. Add several regional languages at once, with separate prompt, check, and font support for each.

## Decision

Choose option 2 behind `ENHANCE_HINDI=off` by default. Preserve the existing extensible language
tag pattern; add `hi` as a selectable UI option only when enabled. Use existing prompt loading,
provider, JSON enforcement, and quality modules. Include target-language anti-hallucination and
prompt-injection guidance in the Hindi prompt rules. Add Hindi starter vocabulary/stop-word lists
to `config/quality_rules.json`, marked as starting versions needing native-speaker review.

For each applicable check, the report will identify it as “English only,” “language-aware,” or
“skipped for this language.” Hindi readability is “not measured”; no English readability formula
score will be presented for Hindi. Do not claim native-speaker review: none has been confirmed.
Document the current PDF Devanagari-font limitation rather than presenting unsupported rendering
as verified.

## Consequences

- Default English generation remains on the existing prompt and schema path.
- Hindi prompts and output require native-speaker review before production use.
- Additional language-specific prompt and quality work is required before enabling another locale.
- Hindi PDF rendering may not display correctly until a suitable licensed font is integrated.
- Mock-mode metrics cannot establish live translation quality or cultural suitability.
