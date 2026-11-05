# Stage 4 Summary

## What Was Built

- Swappable `LLMProvider` abstraction with MockProvider and an OpenAI-compatible hosted provider adapter.
- Versioned prompt files for campaign brief, descriptions, and promotional copy.
- Campaign Brief Builder, Description Generator, Promotional Copy Generator, JSON repair, cache, lightweight checks, and synchronous orchestration.
- Stage 4 API endpoints for brief creation/editing, generation, and description/promo regeneration.
- Streamlit brief review, generation results, warnings, mock-provider indicator, and estimated token usage.
- Audience comparison script and adaptation report.

## Prompt Versions

- `brief_v1`
- `description_v1`
- `promo_v1`

## Mock Mode

Mock mode requires no API key or network connection:

```powershell
$env:LLM_PROVIDER="mock"
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m streamlit run frontend/app.py
```

## Live Mode

Stage 1 named a hosted API but did not select a vendor. Live mode therefore uses an OpenAI-compatible endpoint configured by environment variables:

```powershell
$env:LLM_PROVIDER="hosted"
$env:LLM_API_KEY="set-through-local-environment-only"
$env:LLM_BASE_URL="https://your-approved-provider.example/v1"
$env:LLM_MODEL="approved-model-name"
```

No secrets are stored in source files. Live provider pricing and endpoint behavior require vendor confirmation.

## Test Results

- Full Stage 3 and Stage 4 suite: 53 tests passed.
- Brief builder: 100% coverage.
- Description generator: 95% coverage.
- Promo generator: 100% coverage.
- JSON enforcement: 97% coverage.
- Orchestrator: 82% coverage.
- New-module combined coverage: 92%.
- New JSON schemas and examples validate under Draft 2020-12.
- Live port smoke calls could not run because terminal approval skipped them; API behavior passed through FastAPI TestClient.

## Assumptions

- Stage 4 generation is synchronous, matching the Stage 2 MVP decision where synchronous calls were not contradicted by available sources.
- The hosted provider is vendor-neutral and OpenAI-compatible because Stage 1 did not name a vendor.
- Estimated token usage is planning data and provider-reported usage is used when available.
- In-memory brief and cache storage are used because database/history features are deferred.
- Canned mock output intentionally prioritizes repeatable offline demos over persona-specific live quality.

## Corrections

1. Stage 2 architecture, module specification, API design, prompt design, error-handling plan, and Stage 4 generation schemas are absent from the workspace. Minimal Stage 4 contracts were reconstructed from Stage 1.
2. Stage 1 selected a hosted API generically without naming the provider or model. The live adapter is documented as OpenAI-compatible and is not represented as the unresolved vendor selection.
3. The persona library is unaffected; the water-bottle mock examples use `college_students` for predictable offline output.
4. The Stage 3 persona correction added `Instagram Reels` for `tech_enthusiasts`; preferred formats remain normalized at runtime rather than changing source persona data.

## Open Questions Before Stage 5

1. Approve the exact hosted LLM vendor and model.
2. Confirm production endpoint/base URL and pricing budget.
3. Decide whether 700 ml / pricing values require stronger currency or locale handling.
4. Confirm exact synchronous timeout and campaign token budget.
5. Decide whether brief/cache persistence belongs in Stage 5 or later.

## Stage 5 Preview

Stage 5, Social Media Content, will reuse the campaign brief, validated input, audience profile, prompt loader, provider/cache layer, JSON enforcement, API response conventions, and lightweight warning format from this Stage 4 implementation. It should add platform schemas and social-content prompts without changing brief ownership.

## Suggestions for Later

- Persistent campaign cache and brief storage.
- Provider-native structured-output support.
- Richer copy-to-clipboard browser behavior.
- Per-provider observed token/cost accounting rather than estimates.
