# API Reference

FastAPI serves an interactive OpenAPI reference at `/docs` when the backend is running.

The source API design is maintained in [docs/stage2/openapi.yaml](stage2/openapi.yaml). Running
application endpoints include campaign input, audience, generation, quality, history, package,
section edit/revert, export, asset, and health operations.

Campaign history and export endpoints:

```text
GET /health
GET /personas
POST /inputs/validate
POST /audiences/profile
POST /campaigns
PUT /campaigns/{campaign_id}/brand-kit/logo
GET /campaigns?sort=updated&search=...
GET /campaigns/{campaign_id}/package
PATCH /campaigns/{campaign_id}/sections/{section}
POST /campaigns/{campaign_id}/sections/{section}/revert
POST /campaigns/{campaign_id}/quality
POST /campaigns/{campaign_id}/approve?approved_by=...&report_id=...
POST /campaigns/{campaign_id}/exports
GET /exports/{export_id}
```

The YAML source includes the Stage 9 campaign-history and export operations alongside the earlier
generation, media, and quality routes. Section edits are validated against the corresponding
output schema and mark prior quality reports outdated. Exports are blocked when approval is
required and the latest report is stale or has unresolved critical/major findings.

Validation errors use HTTP 422; missing records use HTTP 404; conflicts such as stale reports
normally use HTTP 409. Responses include route-specific structured error details.

Hindi input is accepted only when `ENHANCE_HINDI=on`. A campaign may include a `brand_kit` in its
inputs only when `ENHANCE_BRAND_KIT=on`; logo uploads use the route above with `image/png`,
`image/jpeg`, or `image/webp` content, and are validated, re-encoded, and stored as campaign assets.
SVG is not accepted. The upload requires an existing campaign brand kit with `rights_confirmed`
set to `true`. These flags default to `off`.

Hindi PDF and ZIP exports return HTTP 422 until a Devanagari-capable font is embedded. DOCX and
JSON exports remain supported.
