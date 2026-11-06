# Configuration Reference

## Files

| File | Purpose |
|---|---|
| `config/platform_rules.json` | Platform character and hashtag limits |
| `config/quality_rules.json` | Quality and claim rules |
| `config/export_settings.json` | Page size, image width, retention, export limits, disclosure |
| `config/visual_formats.json` | Visual output formats |
| `config/video_formats.json` | Video durations and format settings |
| `config/image_safety.json` | Image safety settings |
| `config/voice_options.json` | Available mock/hosted voices |

All API keys and live-provider credentials are secret environment variables. Mock and image limits
are non-secret operational settings.

## Stage 12 feature flags

| Variable | Default | Purpose |
|---|---|---|
| `ENHANCE_HINDI` | `off` | Enables Hindi (`hi`) input, prompt policy, and quality-report annotations. |
| `ENHANCE_BRAND_KIT` | `off` | Enables campaign-scoped colors, font/license notes, rights confirmation, and raster-logo upload. |

Set each flag to exactly `on` or `off`. With the defaults, the Stage 12 features remain disabled.
Uploaded brand logos use the existing local asset storage folder and the `MAX_PRODUCT_IMAGE_BYTES`
upload limit; no separate cloud storage location is introduced. SVG uploads are not supported.
