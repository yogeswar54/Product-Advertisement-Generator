# ADR-E2: Direct Social Posting

- **Status:** Deferred; no direct posting in Stage 12.

## Context

Stage 1 and Stage 6 keep publication outside the MVP, and Stage 5 lists platform publishing
previews as a later possibility. Direct posting requires platform-specific application approval,
OAuth/token handling, user consent, policy monitoring, publishing error recovery, and a clear
human approval boundary. Platform rules and API availability can change independently of this
project.

## Options

1. Add direct posting to social platforms.
2. Add a scheduler integration after platform and security review.
3. Provide a human-controlled export-to-scheduler handoff without API calls.

## Decision

Choose option 3 for design only; implement no scheduler or platform API integration in Stage 12.
The eventual handoff should export the approved campaign content and selected platform/format as a
file or copy-ready package. The user must choose the destination scheduler, authenticate there,
review the final content, and trigger scheduling themselves.

## Consequences

- No platform credentials, tokens, or account permissions are collected.
- Platform approval, consent, account security, and policy risks are not introduced by Stage 12.
- Users retain a manual scheduling step; no claim of direct-publishing functionality is made.
- Any later integration needs a separate ADR, platform-specific approval, consent UX, token
  protection, revocation, audit logging, and failure recovery.
