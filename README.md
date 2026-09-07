# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

A FastAPI + PostgreSQL platform that lets a business create embeddable
lead-capture widgets and safely receive submissions from external websites.

## Architecture

```text
Owner
  |
  v
Authenticated FastAPI
  |
  v
PostgreSQL
  |
  v
Widget
  |
  v
<script src="/widget.v1.js?id=...">

External Website
  |
  v
Widget JavaScript
  |
  v
CORS submission
  |
  v
Validation
  |
  v
Rate limit + honeypot
  |
  v
Geo A -> Geo B -> no geo
  |
  v
PostgreSQL
  |
  v
Background notification