# ADR-E5: Fully Automated Short Video

- **Status:** Deferred.

## Context

Stage 7 generates narration scripts and supports optional TTS and mock FFmpeg assembly. Stage 1
explicitly excludes final video assembly from MVP scope and identifies timing drift as a risk.
Fully automated rendering requires media job operations, licensed assets and voices, output
validation, disclosures, storage lifecycle, and a reliable worker environment.

## Options

1. Automatically render and publish finished videos during campaign generation.
2. Add an explicit user-triggered render workflow using reviewed, licensed assets.
3. Keep the current script and optional preview workflow.

## Decision

Choose option 3 for Stage 12 and defer full short-video generation. A future implementation should
use a separately operated, queued render workflow with user-triggered assembly, duration and
caption checks, rights metadata, and human review before export or publishing.

## Consequences

- No new render workload or asset-rights claims are introduced in this stage.
- Existing script, TTS, and preview behavior remains unchanged.
- A future decision depends on verified FFmpeg deployment, cloud storage, job recovery, and
  measured rendering costs and quality.
