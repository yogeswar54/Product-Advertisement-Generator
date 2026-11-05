# Scope and Risks

## In Scope

- Structured product, audience, campaign, and platform inputs.
- Ten predefined audience personas and custom audience notes.
- Shared campaign brief generation and editing.
- Product descriptions, promotional copy, platform posts, visual prompts, and narration scripts.
- A seven-day social calendar.
- Optional hosted image generation and text-to-speech.
- Length checks, unsupported-claim warnings, export, and draft persistence.

## Out of Scope

- Direct publishing to social networks.
- Campaign ad-account management, paid-media bidding, or analytics.
- Full final video editing, motion design, and rendering in the MVP.
- Live collaborative editing and comments.
- Voice cloning or celebrity-style voices.
- Automated legal clearance or factual certification.
- Accounts and team permissions unless production architecture later expands them.

## MVP Definition

The first release must accept validated inputs, resolve a persona, create and edit a campaign brief, generate all text modules, produce visual concepts, create three narration scripts, run quality checks, and export JSON/Markdown. Optional hosted image generation and TTS may be included if provider integrations are stable and costs are capped.

## Deferred Items

- React/Next.js production UI.
- Full video assembly and rendering workers.
- Additional languages beyond initial English support.
- Custom personas at organization scale.
- Multi-user workspaces, approvals, and version history.
- Social publishing integrations.
- Open-source LLM deployment.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hallucinated product facts | High | High | Generate only from submitted fields; mark missing evidence; run claim checks; require human confirmation. |
| Generic or repetitive copy | Medium | Medium | Require persona-specific hooks, benefit emphasis, and two structurally distinct variants. |
| Inconsistent outputs across modules | Medium | High | Generate all modules from the same campaign brief and test brief-reference coverage in QA. |
| Provider API cost exceeds budget | Medium | High | Set token budgets, usage caps, caching, retries, and model-size configuration. |
| Poor image quality | Medium | Medium | Human-readable quality gate, reference image upload, prompt refinement, and optional regeneration. |
| Copyright, likeness, or asset reuse issue | Medium | High | Do not copy provided brand slogans; flag user assets for source rights; use provider and asset licenses review. |
| Unverifiable advertising claims | High | High | Maintain allowed-claim rules, evidence fields, warning codes, and human approval before export. |
| Toxic, biased, or stereotyped language | Medium | High | Personas describe behavior and needs; add protected-class and stereotype filters; sample-test all personas. |
| Platform rule changes | High | Medium | Store limits as configuration and run scheduled compatibility tests. |
| Model outage or rate limit | Medium | Medium | Provider abstraction, retries with bounded backoff, partial-result export, and clear status. |
| Product image mishandling | Low | High | Validate file type/content, limit size, avoid logging pixels, and apply retention rules. |
| Video or audio drift from script | Medium | Medium | Keep timing metadata canonical and warn when rendered duration differs from target tolerance. |

## Success Criteria

| Measure | MVP Target |
|---|---|
| Human quality rating | Average at least 4 out of 5 across usefulness, tone, and platform fit. |
| Persona adaptation | At least 90% of sampled outputs contain identifiable persona-specific emphasis without stereotypes. |
| Brief consistency | At least 95% of sampled module outputs cite or follow the three brief anchor elements in automated text review. |
| Platform limits | 100% of exported social posts pass configured character limits. |
| Generation time | At least 90% of text-only packages complete in under 60 seconds under normal test load. |
| Hallucination checks | 100% of generated absolute claims that lack supplied evidence are flagged before human review. |
| Reliability | Draft and completed text generation recover without loss after at least 95% of simulated provider/service interruptions. |
| Export completeness | 100% of successful campaign runs contain brief, all requested text modules, quality report, and JSON export. |
| Accessibility | Core form labels and validation errors pass basic keyboard and screen-reader review. |

## Ethical and Compliance Notes

- Health, alcohol, nicotine, financial services, gambling, political advertising, age-restricted products, children-targeted advertising, and other regulated categories require added review or may be blocked.
- Health-benefit claims require appropriate jurisdiction-specific evidence and expert review; the tool must not infer or upgrade those claims.
- Alcohol and nicotine copy should respect legal age restrictions and avoid appealing to minors.
- Financial content must not promise returns, use deceptive urgency, or present generated copy as investment advice.
- Political persuasion and sensitive personal targeting require separate compliance controls and are outside MVP scope.
- Bias checks must avoid protected-group profiling and ensure that personas influence tone through needs and behavior, not stereotypes.
- User-supplied images and copied claims must not be represented as verified until source rights are reviewed.
- Safety-sensitive outputs should contain a clear human-review label and never be auto-published.

## Human Review Gate

Every export must state: “AI-generated draft. Verify facts, rights, platform rules, and local advertising requirements before publication.”
