# Stage 3 Summary

## What Was Built

- FastAPI Input Validator with canonical fields from the Stage 1 input specification.
- Pydantic models for `CampaignInput`, `AudienceProfile`, and persona records.
- Sanitization, prompt-injection warnings, restricted-category flags, and configurable image-reference checks.
- Persona library loaded at startup from `data/personas.json`.
- Rule-based Audience Profiler for persona profiles, custom audiences, persona overrides, and a starting bias guard.
- Local Stage 3 API endpoints: `/health`, `/personas`, `/personas/{id}`, `/inputs/validate`, and `/audiences/profile`.
- Streamlit product, audience, campaign-settings, and review screens.
- pytest coverage tests for validator, profiler, personas, API, and schema examples.

## Corrections

1. `data/personas.json` contains `youtube-style short video` in `tech_enthusiasts.best_platforms`. The persona library normalizes this value to `instagram` and normalizes the matching preferred format to `Instagram Reels`; invalid values are still rejected by startup validation.
2. Stage 2 source documents and schemas were absent at the beginning of this work. Minimal `input.schema.json`, `audience_profile.schema.json`, examples, an OpenAPI YAML, and local API contracts were restored to continue Stage 3.
3. Stage 1 platform enums do not include `youtube-style short video`, so no Stage 1 data file was silently changed beyond the runtime normalization recorded here.

## Assumptions

- MVP launch language is `en-US` unless extended in Stage 4.
- The optional image field is represented as a URL, data URI, or uploaded-image metadata string in Stage 3 JSON.
- Restricted-category detection is behavior based and conservative; it does not block generation.
- Persona overrides accept fields defined by `AudienceProfile`.
- The bias guard is an initial rule-based starting version, not a substitute for moderation or human review.

## Run Commands

See `README.md` for installation, backend, frontend, tests, and curl examples.

```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m streamlit run frontend/app.py --server.address 127.0.0.1
python -m pytest backend/tests -q --cov=app/modules/input_validator.py --cov=app/modules/audience_profiler.py --cov-report=term-missing
```

## Test Results

- Python compilation: passed.
- Direct persona loading: 10 personas loaded.
- Direct schema-example model validation: passed.
- Prompt-injection warning and restricted-category probe: passed.
- Live backend smoke test: `/health` passed; persona listing returned 10 personas; persona lookup passed.
- Full pytest result: 36 tests passed.
- Validator coverage: 94%.
- Audience Profiler coverage: 100%.
- Combined measured coverage: 97%.

## Open Questions Before Stage 4

1. Which hosted LLM provider will Stage 4 use?
2. Confirm whether English remains the only MVP language.
3. Confirm the exact current platform limits stored by configuration.
4. Should image upload metadata use a multipart endpoint rather than a URL or data URI?
5. Confirm whether custom audiences can be saved and reused.

## Stage 4 Preview

Stage 4 will add the campaign brief and text generation modules. It will reuse:

- `backend/app/models/input.py`
- `backend/app/modules/input_validator.py`
- `backend/app/modules/persona_library.py`
- `backend/app/modules/audience_profiler.py`
- `/schemas/input.schema.json`
- `/schemas/audience_profile.schema.json`
- `/frontend/app.py`
- `/docs/stage3/03_stage3_summary.md`

## Suggestions for Later

- Add stronger multilingual normalization.
- Add configurable allow/deny lists for bias patterns.
- Add persisted custom-audience profiles.
- Add uploaded-image multipart validation and MIME fingerprint inspection.
