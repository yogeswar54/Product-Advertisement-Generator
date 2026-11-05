# Social Platform and Audience Adaptation Report

## Source

All comparison results below use the offline deterministic MockProvider. No real LLM call or API key was configured for this report.

## Platform Differences

| Platform | Observed format | Mock length/tone |
|---|---|---|
| Instagram | Caption, hashtag set, carousel ideas, and Reel hook | Visual, short, campus-oriented |
| LinkedIn | Professional value statement and light hashtags | Formal and benefit-oriented |
| X/Twitter | Single concise post | Direct and shortest |
| Facebook | Community-style paragraph plus a question | Longer and conversational |
| WhatsApp | Short promotional message with a CTA and details | Personal and action-oriented |

The mock provider clearly differentiates length and format across the platforms. The calls are not copies of one sentence.

## Audience Differences

The Instagram captions produced by the mock for College Students, Young Professionals, Working Parents, and Fitness Enthusiasts were identical. This is a limitation of the canned provider, not evidence that audience adaptation works. Persona prompts, platform rules, and few-shot files exist for live providers; a real LLM rerun is required to assess audience adaptation reliably.

## Assessment

Platform block structure reads clearly different. Audience-specific output is not sufficiently differentiated in mock mode, so mock parity is acceptable for deterministic demo and schema tests but not considered a successful adaptation evaluation. Before production acceptance, run a live provider with each persona and compare tone, vocabulary, benefit angle, slang, and avoidances. Improve the audience and few-shot blocks if live captions remain generic.
