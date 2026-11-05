# Technology Stack Decision

Costs are rough planning estimates for a small MVP and can change. They exclude labor, taxes, and outbound transfer unless noted.

## Frontend Options

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| Streamlit / Gradio | Fastest prototype; Python-native; built-in forms and file handling | Less control over dense workflows, branding, and interactions | Hosting often $0-$50/month for a small app; usage-based compute | Low |
| React / Next.js | Flexible UI, strong production ecosystem, responsive workflow design | More frontend/backend integration work and deployment configuration | $20-$100+/month to start depending on hosting | Medium |

**Decision:** MVP uses Streamlit. Production recommends React/Next.js when user-facing workflow depth or a production design system is required.

## Backend

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| FastAPI | Fast async API, Python ecosystem, OpenAPI, straightforward orchestration and LLM integration | Requires separate API/UI deployment and careful async/provider timeouts | Hosting $20-$100+/month at small scale | Low-Medium |

**Decision:** FastAPI for both MVP and production.

## Text LLM

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| Hosted API | Fast setup, strong quality, maintained models, scalable | Usage fees and provider dependency | Roughly $0.01-$0.10 per text package depending on provider, prompt size, and model | Low |
| Open-source model | Data control, predictable long-run compute cost, flexible deployment | Hosting/GPU operations, lower-quality variance, prompt tuning | Small GPU host roughly $100-$1,000+/month depending on model and uptime | High |

**Decision:** Hosted API for MVP; production may mix hosted and open-source providers behind a provider abstraction. An open-source path is worth selecting only if privacy, volume, or latency justifies operating cost.

## Image Generation

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| Hosted image API | Fast quality iteration, no GPU operations, prompt safety features vary | Per-image fees, content-policy dependency, licensing review | Roughly $0.02-$0.20/image depending on provider and resolution | Low |
| Open-source local/self-hosted diffusion | More control and no per-image fee for frequent use | GPU cost, model licensing, moderation, slower operations | GPU host from roughly $100/month upward; higher for dedicated use | High |

**Decision:** MVP uses prompt generation plus optional hosted image generation. Production keeps provider selection configurable and blocks unsupported claims in prompts.

## Text-to-Speech

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| Hosted neural TTS | Natural voices, simple API, many languages | Character charges, voice licensing and consent policies | Roughly $4-$20 per million characters depending on provider tier | Low |
| Custom trained voice | Brand differentiation and consistency | Consent, data processing, IP, and retraining burden | Often expensive; unsuitable for MVP | High |

**Decision:** Hosted TTS in MVP with configurable voices, no cloned voice support. Production adds regional voice settings and usage caps.

## Video Assembly

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| FFmpeg | Fast, scriptable, low cost, strong format control | Complex filter debugging; less Python timeline abstraction | Compute only | Medium |
| MoviePy with FFmpeg | Easier Python composition and timeline code | Wrapper overhead and less control for edge cases | Compute only | Medium |

**Decision:** FFmpeg for production rendering; MoviePy may be used in the MVP for simple preview assembly if enabled. Automatic final video assembly is deferred.

## Database and Storage

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| SQLite + local object storage | Zero setup for MVP and easy local export | Weak concurrent scale and backup automation | Almost no direct cost in local MVP | Low |
| PostgreSQL + object storage (S3-compatible or Blob) | Transactions, indexing, managed backups, scalable assets | More operations, schema and IAM setup | Database $10-$100+/month; storage often $0.02-$0.10/GB/month | Medium |

**Decision:** PostgreSQL and managed object storage for production; SQLite is acceptable only for isolated MVP trials and must support JSON export. Production asset storage should separate public previews from private source uploads.

## Deployment

| Option | Pros | Cons | Estimated cost | Difficulty |
|---|---|---|---|---|
| Simple PaaS container/app service | Fast deployment, built-in TLS and scaling | Less network/control customization | $20-$150+/month for small services | Low-Medium |
| Kubernetes | Fine-grained scaling and service isolation | Significant operations overhead for MVP | Typically $150-$500+/month before optimization | High |

**Decision:** MVP deploys Streamlit and FastAPI to a small managed PaaS/container platform. Production starts with managed containers and managed PostgreSQL; Kubernetes is deferred unless scale or isolation requires it.

## Recommended MVP Stack

- Frontend: Streamlit.
- Backend: FastAPI.
- Text: one hosted text LLM.
- Images: optional hosted image generation.
- Audio: optional hosted neural TTS.
- Video: no assembly in MVP; MoviePy/FFmpeg previews only if a later MVP extension is approved.
- Data: SQLite for a single-instance MVP, with export; PostgreSQL migration planned.
- Storage: local or managed object storage for temporary image/audio files.
- Deployment: managed container or app service.
- Estimated baseline: roughly $30-$100/month for light hosting plus usage fees, with provider cost subject to prompt and asset volume.

## Recommended Production Stack

- Frontend: React/Next.js.
- Backend: FastAPI services behind managed API gateway/load balancing.
- Text: hosted primary provider plus provider abstraction; optional open-source fallback for approved workloads.
- Images: hosted provider with moderation and asset rights review; configurable alternative provider.
- Audio: hosted neural TTS with usage controls, no voice cloning.
- Video: FFmpeg workers triggered by queues, asset storage, and job status tracking.
- Data: PostgreSQL with managed backups and migrations.
- Storage: S3-compatible object storage with lifecycle rules and private buckets.
- Deployment: managed containers, autoscaling, observability, and secret manager.
- Estimated baseline: roughly $150-$500+/month before text, image, TTS, and media rendering usage.

## Cross-Stack Decisions

- Use JSON schemas and campaign-brief objects in both stacks.
- Store provider credentials in a secret manager or environment variables outside source control.
- Implement timeouts, retries with caps, provider health checks, and usage budgets.
- Keep UI copy generation decoupled from assets so text failures remain recoverable.
