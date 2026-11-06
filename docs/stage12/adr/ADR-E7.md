# ADR-E7: PostgreSQL and Cloud Object Storage

- **Status:** Deferred to production-readiness work.

## Context

Stage 1 recommends PostgreSQL and managed object storage for production, while allowing SQLite
and local files for the MVP. Stage 9 implements SQLite and local storage. Stage 6 and Stage 7
summaries identify cloud asset/media storage as future work. Moving storage safely needs explicit
migrations, backup/restore evidence, private-bucket and IAM policies, retention rules, and
deployment validation.

## Options

1. Migrate the current default immediately to managed PostgreSQL and a named cloud vendor.
2. Add a storage abstraction and run a tested migration to a selected managed PostgreSQL and
   S3-compatible service when a production environment is approved.
3. Keep SQLite and local files for the current local, single-instance workflow.

## Decision

Choose option 3 for Stage 12 and plan option 2 as a production prerequisite. Do not select or claim
a cloud vendor, price, or deployment status without an approved target and operational evidence.

## Consequences

- Stage 12 features use the campaign persistence and configured local asset storage already
  present.
- Multi-instance deployment, managed backup guarantees, and cloud durability are not claimed.
- Before migration, validate schema/data migrations, integrity, private access, IAM least
  privilege, retention/deletion, backup restore, and rollback.
