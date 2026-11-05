# Stage 6 Summary

## What Was Built

- Configurable visual formats for poster, banner, story, and square social posts.
- Three-concept Visual Concept Generator with versioned prompts and JSON repair.
- Palette and WCAG contrast helpers plus lightweight visual safety checks.
- Mock and hosted-compatible image provider adapters.
- Local PNG asset storage, metadata, safe serving, and cleanup utility.
- Stage 6 visual regeneration and user-triggered image-generation APIs.
- Streamlit Visuals tab with concept cards, swatches, prompts, image controls, and overlays.
- Four-persona visual comparison script.

## Prompt Versions

- `visual_concepts_v1`
- `image_prompt_v1`

## Orchestration Choice

Visual concepts use the campaign brief only and run in parallel with description, promo, and social generation. Promo headlines are not prerequisites. A promo headline may be injected when available, but visual generation remains valid without a successful promo module.

## Mock Mode

```powershell
$env:LLM_PROVIDER="mock"
$env:IMAGE_PROVIDER="mock"
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m streamlit run frontend/app.py
```

## Live Mode

Stage 1 selected hosted image generation without naming a vendor. The adapter is vendor-neutral OpenAI-compatible and expects approved environment settings:

```powershell
$env:LLM_PROVIDER="hosted"
$env:IMAGE_PROVIDER="hosted"
$env:IMAGE_API_KEY="set-through-local-environment-only"
$env:IMAGE_API_BASE_URL="approved-provider-base-url"
$env:IMAGE_MODEL="approved-image-model"
```

## Test Results

- Full Stages 3-6 suite: 91 tests passed.
- Stage 6 focused suite: 19 tests passed.
- Stage 6 new-module coverage: 86%.
- Visual schema and example validate under Draft 2020-12.
- Mock placeholder images are validated PNG files at configured format dimensions.
- Live image provider calls were not run because no live key was configured.

## Assumptions

- Format sizes are configurable defaults and require current platform verification.
- The default campaign image limit is an estimated project control of 4 images; request limit is 1 in this stage.
- Mock concepts use generic product appearance and state that an uploaded image is preferred.
- Contrast warning threshold is WCAG normal-text guidance at 4.5:1.

## Corrections

1. Stage 2 visual/API/data documents and the Stage 6 visual schema were absent. Minimal contracts were reconstructed from Stage 1 and the Stage 6 attachment.
2. Stage 1 did not name an image vendor, so a vendor-neutral hosted-compatible adapter is used.
3. Product appearance remains generic unless the optional image note/reference is supplied.
4. The prompt loader now accepts underscored prompt names such as `visual_concepts_v1`.

## Open Questions Before Stage 7

1. Approve the live image vendor and model.
2. Confirm copyright/licensing rules for generated assets.
3. Confirm image retention and campaign metadata limits.
4. Confirm current platform dimensions.
5. Decide whether Stage 7 video scenes use all visual concepts or only the selected concept.

## Stage 7 Preview

Stage 7 Video Script and Narration will reuse visual concepts, image prompts, campaign brief, audience profile, provider abstraction, asset metadata, JSON repair, caching, and API conventions. It will add 15/30/60-second scripts and optional TTS without final video assembly in the MVP.

## Suggestions for Later

- Image reference-image support for approved providers.
- Cloud asset storage.
- Persistent image metadata database.
- Automatic design-tool overlay export.
