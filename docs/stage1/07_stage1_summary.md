# Stage 1 Summary

## One-Page Decision Summary

The AI-Based Product Advertisement Generator is planned as a structured campaign assistant for small business owners, freelancers, marketing students, solo creators, and lean marketing teams. It accepts product facts, a brand voice, campaign goal, language, platforms, and an audience persona, then creates a single campaign brief that governs descriptions, promotional copy, social content, visual concepts, and narration scripts. Human review is mandatory because generated outputs are drafts and may not contain verified claims.

Stage 1 uses explicit canonical names such as `product_name`, `campaign_brief`, `key_benefits`, and the persona ID set in `data/personas.json`. The MVP is text-first: FastAPI performs orchestration, Streamlit provides the quickest interface, and a hosted LLM supplies text. Hosted image generation and neural TTS are optional integrations, while final video assembly is deferred. Production can move to React/Next.js, PostgreSQL, managed object storage, provider abstraction, and managed container deployment.

The MVP prioritizes a complete package, brief consistency, platform limits, factual claim checks, JSON export, and recoverable drafts. Final publishing, ad accounts, collaborative editing, voice cloning, additional languages, and long-form video rendering remain out of scope. Success is measured through human ratings, persona adaptation, platform compliance, generation time, complete exports, and claim-check coverage.

## Stage 1 Done Checklist

| Done criterion | Status |
|---|---|
| Folder structure created exactly as requested | Done |
| Project vision and problem statement documented | Done |
| Target tool users defined | Done |
| Functional requirements numbered and grouped | Done |
| Non-functional requirements numbered and prioritized | Done |
| Every requirement mapped to MoSCoW priority | Done |
| All canonical inputs defined and validated | Done |
| All text, social, visual, video, and export outputs defined | Done |
| Campaign brief structure documented | Done |
| Sample input and shortened output JSON provided | Done |
| Ten personas documented consistently | Done |
| Personas represented in valid JSON | Done |
| Water bottle headlines compared across four personas | Done |
| Twenty original sample ads created across at least five categories | Done |
| MVP and production stacks compared and recommended | Done |
| Scope, deferred scope, risk register, and success criteria documented | Done |
| Ethical and compliance constraints documented | Done |

## Open Questions Before Stage 2

1. Which hosted text LLM provider and account will be used?
2. Is the MVP's launch language exclusively English or a specific additional language too?
3. Should optional image generation and TTS be included in the first deploy, or remain hidden feature flags?
4. Which managed deployment platform is approved: Azure, AWS, Google Cloud, or another provider?
5. Is campaign draft data expected to persist only locally, or in a managed database immediately?
6. Which target platforms are in the MVP's exact length and formatting configuration?
7. Are paid product claims or restricted product categories expected in early testing?
8. Which brand/logo/logo-safe image restrictions are mandatory for the production UI?

## Stage 2 Input Preview

Stage 2, System Design, should use this Stage 1 package to produce:

- system context and container/component diagrams;
- API and module contracts derived from the canonical JSON fields;
- campaign brief state transitions and regeneration rules;
- provider adapter interfaces and failure behavior;
- database schema and retention policy;
- platform configuration tables and validation rules;
- prompt architecture and quality-check evidence model;
- security, privacy, logging, and secrets design;
- deployment topology, cost monitoring, and scaling plan;
- an implementation backlog mapped to FR/NFR IDs.
