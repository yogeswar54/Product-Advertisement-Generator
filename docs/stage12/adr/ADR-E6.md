# ADR-E6: User Accounts and Team Review Roles

- **Status:** Deferred.

## Context

The Stage 1 assumptions describe one campaign owner at a time and leave accounts/team approvals
out of scope. Stage 9 persists campaign and approval data but does not provide authentication,
ownership isolation, or authorization. Introducing accounts without these controls could expose
campaigns or allow unauthorized edits and approvals.

## Options

1. Add local username/password authentication and roles directly to the current app.
2. Design a production identity-provider integration, tenant/campaign ownership model, and
   least-privilege review roles.
3. Defer accounts and keep the single-owner local workflow.

## Decision

Choose option 3 for Stage 12. Revisit option 2 only with a threat model, identity provider,
authorization policy, session/token lifecycle, recovery and deletion flows, audit plan, and privacy
review.

## Consequences

- No account credentials or personal profile data are collected.
- Campaign endpoints remain appropriate only for the current single-owner local deployment model;
  they must not be presented as multi-tenant secure.
- A future release must add ownership checks to every read, edit, export, asset, approval, and
  deletion operation before exposing the service to multiple users.
