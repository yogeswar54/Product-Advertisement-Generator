# Stage 12 Enhancement Roadmap

## Purpose and scoring method

This roadmap evaluates the seven candidate enhancements recorded across the earlier stages. Every
score below is a **planning judgment, not a measurement**. User value is rated 1–5 (5 is highest).
Technical effort and risk are rated 1–5 (5 is highest). Cost impact is a relative estimate of
incremental operating cost, rated 1–5 (5 is highest); it is not a vendor quote or measured cost.
Risk notes cover the relevant legal, privacy, platform-policy, and output-quality considerations.

| ID | Enhancement | User value (judgment) | Technical effort (judgment) | Cost impact (judgment; estimate only) | Risk (judgment; legal/privacy/platform/quality) | Dependencies on earlier stages | Recommendation |
|---|---|---:|---:|---|---|---|---|
| E1 | Hindi and other regional language support | 4/5 | 4/5 | 2/5, low to moderate incremental usage and font cost | 4/5; translation accuracy, regulated claims, and quality checks need language-aware review | Stage 1 NFR-11; Stage 3 input and audience profile; Stage 4–7 generation prompts; Stage 8 quality; Stage 9 exports; Stage 10 evaluation | **Build now:** Hindi only, behind `ENHANCE_HINDI=off` by default |
| E2 | Direct posting to social platforms | 4/5 | 5/5 | 4/5, estimated high ongoing integration and operations cost | 5/5; platform approval/policy, explicit consent, account-token security, and publishing liability | Stage 5 social content; Stage 8 approval; Stage 9 package/export; Stage 11 deployment and secrets | **Do not build in this stage.** Keep an export-to-scheduler handoff design; no platform API calls |
| E3 | Performance feedback loop from engagement data | 4/5 | 4/5 | 3/5, estimated moderate storage and analysis cost | 5/5; privacy and bias risks; any future input must be aggregate, user-entered metrics only, with no personal data | Stage 5 social outputs; Stage 9 campaign persistence; Stage 10 evaluation and metrics | **Build later,** after privacy boundaries and an evaluation baseline are agreed |
| E4 | Per-campaign brand kit for visuals and exports | 4/5 | 4/5 | 2/5, estimated low to moderate storage and rendering cost | 3/5; logo/font rights remain unverified, uploads need safe processing, and overlays need contrast checks | Stage 3 image validation; Stage 6 palette/contrast and visual concepts; Stage 9 asset persistence and DOCX/PDF export | **Build now:** opt-in and campaign-scoped, behind `ENHANCE_BRAND_KIT=off` by default |
| E5 | Fully automated short video generation | 4/5 | 5/5 | 5/5, estimated highest media compute and storage cost | 4/5; asset/voice licensing, disclosure, claims, and rendered-output quality | Stage 6 visual assets; Stage 7 narration/TTS/FFmpeg/jobs; Stage 8 quality; Stage 9 persistence/export | **Build later,** after media rights, runtime, and output-quality validation |
| E6 | Real user accounts and team review roles | 4/5 | 5/5 | 4/5, estimated high identity and support cost | 5/5; personal data, authorization errors, shared-campaign exposure, and retention obligations | Stage 9 campaign ownership and approval; Stage 10 security; Stage 11 production deployment | **Build later,** with a production identity, authorization, and privacy design |
| E7 | PostgreSQL migration and cloud object storage | 4/5 | 4/5 | 4/5, estimated moderate to high managed-service and operations cost | 4/5; IAM, data location, retention, backups, and migration integrity | Stage 9 SQLite/local assets; Stage 10 reliability; Stage 11 deployment | **Build later,** before multi-instance production as required by the Stage 1 production-stack decision |

## Stage 12 selection

Implement E1 (Hindi) and E4 (brand kit), and no other enhancement. These have high expected user
value while reusing existing input validation, prompt loading, audience profiles, quality rules,
visual palette/contrast checks, campaign persistence, and export code. Both can be explicitly
disabled by default. E1 is limited to Hindi in this stage; regional languages beyond Hindi are not
included. E4 is limited to a per-campaign kit and a user-uploaded raster logo; font and logo rights
are not independently verified.

The feature flags must be evaluated explicitly. With either flag off, the existing English/default
campaign flow and campaign exports must remain unchanged. The feature flags are not a substitute
for validating the supplied campaign data.

## Candidate dependencies from earlier stages

The formal “Suggestions for Later” sections are in the Stage 3–7 summaries. Their relevant items
include stronger multilingual normalization (Stage 3); platform publishing previews, persistent
scheduling, and analytics-based calendar optimization (Stage 5); design-tool overlay export and
cloud asset storage (Stage 6); and cloud media storage/transcoding (Stage 7). The Stage 8–11
summaries do not contain a formal section with that heading. E2–E7 also reflect the broader deferred
items and production decisions in the Stage 1 and Stage 9–11 documents.

## Guardrails and non-goals

- E2 has no direct platform integration or posting on a user's behalf. Any later scheduler flow
  should export a human-approved package and leave final scheduling to the user or a separately
  approved scheduler.
- E3 is not implemented. If revisited, accept aggregate, user-entered engagement counts only; do
  not collect names, handles, comments, audience identifiers, or other personal data.
- Hindi output, translations, generated assets, and quality checks are not certified. Native-speaker
  and legal review remain necessary.
- Brand kit controls record a user confirmation; they do not prove ownership or licensing.
- Estimates are judgments only. No provider pricing or live performance result is implied.

## Corrections to source assumptions

- The current `schemas/input.schema.json` language field is an extensible language-tag pattern, not
  an enum. Stage 12 will preserve its extensibility and add a Hindi UI option without restricting
  existing language-tag values.
- The Stage 2 architecture, module, data-model, API-design, and quality-layer documents named in
  the Stage 12 request are not present in this checkout. Only `docs/stage2/openapi.yaml` exists;
  Stage 3 and subsequent summaries also record that the Stage 2 sources were missing and contracts
  were reconstructed.
- The local Git checkout has no `v1.0.0` tag, and its changelog currently says “Unreleased.” Stage
  12 will not create or alter a tag.
