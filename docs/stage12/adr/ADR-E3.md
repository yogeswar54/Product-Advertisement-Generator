# ADR-E3: Engagement Feedback Loop

- **Status:** Deferred.

## Context

Stage 5 suggests optimizing the calendar from analytics, and Stage 10 reports mock quality
limitations but no human or live-provider results. Engagement feedback could help users compare
their campaigns, but automated collection of handles, comments, audience characteristics, or
platform account data would introduce privacy, consent, and bias risks.

## Options

1. Import or collect platform-level user and audience analytics.
2. Store only aggregate, user-entered campaign metrics.
3. Defer feedback until privacy and evaluation requirements are established.

## Decision

Choose option 3 for Stage 12. If E3 is revisited, constrain it to aggregate, user-entered counts
(for example, totals entered by the campaign owner). Do not collect names, handles, comments,
individual-level events, audience identifiers, or platform credentials.

## Consequences

- No personal data is collected for E3 in Stage 12.
- No feedback model or performance claim is introduced.
- A future design must define aggregation, retention, deletion, user notice, and safeguards against
  treating correlation as causal campaign effectiveness.
