# Design

## Problem

Businesses need a simple way to embed lead-capture forms into websites without building and maintaining their own backend submission system.

## Tenancy

Every user belongs to exactly one tenant.

Every widget belongs to a tenant.

Every submission belongs to both a widget and tenant.

Authenticated queries always filter by tenant_id.

## Widget flow

Owner -> Authenticated FastAPI -> PostgreSQL -> Widget -> Embed snippet

Customer Website -> widget.v1.js -> GET /widgets/{id}/config -> Render form -> POST /submissions

## Submission flow

Request -> CORS -> Pydantic validation -> Rate limiting -> Honeypot -> Geo provider A -> Geo provider B fallback -> no geo -> PostgreSQL -> Notification job

## Idempotency

The optional Idempotency-Key header is stored per widget. Repeating the same key returns the original submission rather than creating another row.

## Background work

Notifications are persisted as jobs. The worker retries failed jobs up to three times. Permanent failure is logged.

Notification failures are isolated from the lead submission path so that a notification problem does not cause an otherwise successful lead submission to fail.

## Caching

The widget JavaScript is versioned as widget.v1.js and served with long-lived immutable caching.

Widget configuration is served separately and cached for a shorter period, allowing configuration changes without changing the JavaScript asset.

## Non-goal

This project does not attempt to become a full visual form builder, marketing automation platform, or production CDN.
