# BUILDLOG

## Phase 1 — Design

AI assistance was used to translate the capstone requirements into:
- database models
- API contracts
- tenant isolation rules
- widget delivery flow
- lead submission flow
- deployment structure

Human verification:
- requirements were checked against the capstone brief
- architecture was simplified to keep the implementation focused
- security and tenant-isolation requirements were reviewed

## Phase 2 — Core platform

AI assistance was used for:
- FastAPI route structure
- PostgreSQL persistence
- Pydantic validation
- authenticated widget CRUD
- tenant isolation
- CORS configuration
- rate limiting
- honeypot protection
- idempotency
- geo-provider fallback
- notification job persistence

Human verification:
- API endpoints were exercised manually
- authenticated CRUD behavior was verified
- invalid input was tested
- cross-tenant access was tested
- rate limiting was intentionally triggered
- honeypot behavior was verified
- idempotency behavior was verified

## Phase 3 — Embeddable widget

AI assistance was used for:
- versioned widget JavaScript
- public widget configuration endpoint
- cross-origin browser integration
- cache headers
- customer test page

Human verification:
- customer site was served from a separate origin
- widget rendered successfully
- browser submission succeeded
- CORS and preflight behavior were verified

## Phase 4 — Reliability

AI assistance was used for:
- background notification processing
- retry handling
- failure logging
- notification side-effect isolation

Human verification:
- notification enqueue failure was deliberately simulated
- lead submission still succeeded
- normal notification behavior was restored
- notification job processing was verified

## Phase 5 — Evidence and documentation

AI assistance was used for:
- organizing implementation evidence
- README and architecture documentation
- test and verification structure

Human verification:
- Docker services were started and checked
- health endpoint was verified
- authenticated CRUD was verified
- tenant isolation was verified
- cross-origin widget behavior was verified
- rate limiting was verified
- honeypot protection was verified
- idempotency was verified
- notification failure isolation was verified

## AI usage disclosure

AI was used as a development assistant for architecture, implementation guidance, debugging, code drafting, documentation, and test planning.

Human verification was performed throughout the build. Application behavior was tested against the running FastAPI and PostgreSQL services, including intentional failure cases.

The final repository and evidence should represent only functionality that was actually implemented and verified.
