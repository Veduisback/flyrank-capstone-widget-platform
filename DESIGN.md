# Design

## Problem

Businesses need a simple way to embed lead-capture forms into websites
without building and maintaining their own backend submission system.

## Tenancy

Every user belongs to exactly one tenant.

Every widget belongs to a tenant.

Every submission belongs to both a widget and tenant.

Authenticated queries always filter by tenant_id.

## Widget flow

```text
Owner
  |
  | authenticated
  v
Widget Management API
  |
  v
PostgreSQL
  |
  v
Embed snippet

Customer Website
  |
  v
widget.v1.js
  |
  v
GET /widgets/{id}/config
  |
  v
Render form
  |
  v
POST /submissions

Submission flow
Request
  |
  v
CORS
  |
  v
Pydantic validation
  |
  v
Rate limiting
  |
  v
Honeypot
  |
  v
Geo provider A
  |
  +-- failure --> Geo provider B
  |
  +-- failure --> no geo
  |
  v
PostgreSQL
  |
  v
Notification job
Idempotency

The optional Idempotency-Key header is stored per widget.

Repeating the same key returns the original submission rather than
creating another row.

Background work

Notifications are persisted as jobs.

The worker retries failed jobs up to three times.

Permanent failure is logged.

Non-goal

This project does not attempt to become a full visual form builder,
marketing automation platform, or production CDN.


---

# 26. `BUILDLOG.md`

```markdown
# BUILDLOG

## Phase 1 — Design

AI assistance was used to turn the capstone requirements into:
- database models
- API contracts
- tenant isolation rules
- submission flow
- deployment structure

Human verification:
- requirements checked against the capstone brief
- architecture simplified to keep the core scope manageable

## Phase 2 — Hardened submission path

AI assistance was used for:
- FastAPI route structure
- Pydantic validation
- CORS configuration
- rate limiting
- honeypot implementation
- geo fallback
- notification queue

Human verification:
- tests and curl requests are used to verify behavior
- failure paths are intentionally exercised

## Phase 3 — Delivery and dashboard

AI assistance was used for:
- versioned widget JavaScript
- cache headers
- customer test page
- dashboard aggregation queries
- Docker setup
- documentation

Human verification:
- second-origin browser test
- API smoke tests
- tenant isolation test
- rate-limit test
- fallback test

The brief specifically requires an honest AI-usage log