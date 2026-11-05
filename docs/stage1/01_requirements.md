# Stage 1 Requirements

## 1. Project Vision

### Vision
AI-Based Product Advertisement Generator turns basic product information into a consistent, audience-adapted advertising package that a non-specialist can edit and publish.

### Problem Statement
Small businesses, freelancers, marketing students, and lean marketing teams often lack the time, budget, or platform expertise to create polished copy, social calendars, visual directions, and short video scripts for several audiences. The result is repetitive work, inconsistent messages, weak adaptation across platforms, and missed publishing deadlines. The product centralizes audience selection, campaign planning, and channel-specific generation in one workflow.

### Target Users
- Small business owners creating ads without an in-house marketing team.
- Freelancers preparing campaigns for multiple clients.
- Marketing students learning and practicing campaign development.
- Solo content creators producing reusable promotional packages.
- Lean marketing teams who need drafts quickly for human review.

## 2. Functional Requirements

### Input Module
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Accept the fields defined in `02_input_output_spec.md`: `product_name`, `category`, `key_features`, `price`, `usp`, `brand_name`, `brand_voice`, `target_audience`, `campaign_goal`, `platforms`, `language`, `product_image`, and `competitor_info`. | Must |
| FR-02 | Validate required fields, file types, maximum lengths, and supported enum values before generation. | Must |
| FR-03 | Allow saving and loading an input draft so work can resume. | Should |

### Audience Profiler Module
| ID | Requirement | Priority |
|---|---|---|
| FR-04 | Resolve a selected audience to a persona in `data/personas.json` and expose its motivations, pain points, objections, tone, triggers, platforms, formats, and avoidances. | Must |
| FR-05 | Support custom audience notes alongside a predefined persona without overriding the persona silently. | Could |

### Campaign Brief Builder Module
| ID | Requirement | Priority |
|---|---|---|
| FR-06 | Build one campaign brief containing `core_message`, `tone`, `emotional_hook`, `key_benefits`, `audience_profile_reference`, and `dos_and_donts`. | Must |
| FR-07 | Use the same campaign brief object as the source of truth for every generated module. | Must |
| FR-08 | Let a user review and edit the campaign brief before downstream generation. | Should |

### Description Module
| ID | Requirement | Priority |
|---|---|---|
| FR-09 | Generate short, medium, and long product descriptions aligned to the selected persona and brief. | Must |
| FR-10 | Enforce module-defined word ranges and avoid unsupported product facts. | Must |

### Promotional Text Module
| ID | Requirement | Priority |
|---|---|---|
| FR-11 | Generate headline, tagline, platform-neutral ad copy, CTA, and two or more A/B variants. | Must |
| FR-12 | Generate distinct variants that differ in hook, benefit emphasis, or proof style rather than only minor wording changes. | Should |

### Social Media Module
| ID | Requirement | Priority |
|---|---|---|
| FR-13 | Generate platform-specific posts for Instagram, LinkedIn, X/Twitter, Facebook, and WhatsApp based on selected platforms. | Must |
| FR-14 | Generate a 7-day content calendar with platform, format, topic, caption, CTA, and posting order. | Must |
| FR-15 | Enforce platform character limits and recommended hashtag counts. | Must |

### Visual Concepts Module
| ID | Requirement | Priority |
|---|---|---|
| FR-16 | Generate visual concepts containing scene, mood, color palette, typography, layout, and image prompt. | Must |
| FR-17 | Generate at least one safe prompt suitable for an image-generation service when image generation is enabled. | Should |

### Video Module
| ID | Requirement | Priority |
|---|---|---|
| FR-18 | Generate 15-second, 30-second, and 60-second narration scripts with matching scene tables. | Must |
| FR-19 | Include voice-over text, estimated word count or duration, scene timing, visual direction, and on-screen text. | Must |
| FR-20 | Generate text-to-speech audio as an optional MVP service when configured by the user. | Could |
| FR-21 | Assemble preview videos from generated scenes, voice-over, captions, and licensed assets. | Won't |

### Quality Check Module
| ID | Requirement | Priority |
|---|---|---|
| FR-22 | Check word and character limits, required fields, unsupported absolute claims, duplicate copy, persona consistency, and empty sections. | Must |
| FR-23 | Flag uncertain claims for human verification rather than silently rewriting them. | Must |
| FR-24 | Produce a quality report showing passed checks, warnings, and actionable fixes. | Should |

### Export Module
| ID | Requirement | Priority |
|---|---|---|
| FR-25 | Export the complete package as structured JSON. | Must |
| FR-26 | Export human-readable Markdown and a ZIP bundle containing generated text and available assets. | Should |
| FR-27 | Support campaign history, versioning, and selective regeneration of modules. | Won't |

### MoSCoW Coverage for Every Functional and Non-Functional Requirement
The priorities above use Must/Should/Could/Won't. NFR priorities appear in Section 3.

## 3. Non-Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-01 | In MVP, a text-only package excluding video audio should complete within 60 seconds under an estimated normal-load API call pattern. | Must |
| NFR-02 | Video narration generation should complete within 45 seconds for all three durations under the same conditions. | Should |
| NFR-03 | The system should spend no more than an estimated $0.10 per text-only MVP generation at default usage rates; providers are subject to change. | Should |
| NFR-04 | A failed optional service such as image generation or TTS must not discard successfully generated text. | Must |
| NFR-05 | Generated campaign data must be recoverable from a saved draft after service interruption. | Must |
| NFR-06 | Production should target 99.5% monthly availability for the API. | Could |
| NFR-07 | Inputs, outputs, API keys, and saved campaigns must be encrypted in transit; secrets must not appear in logs. | Must |
| NFR-08 | No generated text or asset may be presented as medical, legal, financial, or other verified advice unless human-approved. | Must |
| NFR-09 | Generation prompts and QA rules must screen restricted subjects and demographic proxies for harmful stereotypes. | Must |
| NFR-10 | Plain-language labels and validation messages must allow first-time users to complete a campaign with no training. | Should |
| NFR-11 | Core text generation should support English and at least one additional language in production. | Could |
| NFR-12 | The interface should retain content and prevent accidental loss when validation fails. | Must |
| NFR-13 | Logs must not retain product image content or full user prompts longer than necessary for troubleshooting. | Should |
| NFR-14 | Text generation providers should be replaceable through a provider abstraction. | Should |
| NFR-15 | MVP data should be portable in documented JSON or CSV formats. | Should |

## 4. Assumptions

1. Text generation uses an external hosted LLM for the MVP; factual grounding is limited to user-entered facts.
2. The MVP is used by one campaign owner at a time; collaborative editing is not required.
3. Platform limits and content-format recommendations are reviewed at implementation time and stored as configuration.
4. Human review is mandatory before publishing.
5. Generated visual and audio content is a creative draft, not guaranteed to be final-production-ready.
6. Personal data is unnecessary except for account/contact details if the deployment later supports accounts.
7. English is the MVP launch language.
8. Estimated response times and costs are planning targets, not provider guarantees.

## 5. Constraints

- Stage 1 must contain documentation and decisions only; no executable application code, framework setup, or UI implementation is included.
- Product claims may use only information supplied by the user unless a verifiable source is attached and reviewed.
- Output generation depends on third-party availability, usage limits, privacy terms, and pricing.
- Platform character limits, image ratios, and API capabilities may change after Stage 1.
- The MVP should remain buildable by a small team, with provider configuration kept outside source code.
- Compliance interpretation varies by jurisdiction; the product provides warnings, not legal certification.
