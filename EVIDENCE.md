# EVIDENCE

## 1. Layered architecture

Evidence:
- app/routes contains HTTP routes
- app/services contains business logic
- app/db.py handles persistence

## 2. Boundary validation

Command:

```text
POST /submissions
{
  "widget_id": "not-a-uuid"
}
## Verified Test Results

### Docker and API Health
- PostgreSQL container: running
- FastAPI container: running
- GET /health: 200 OK
- Response: {"status":"ok"}

### Authenticated Widget CRUD
- Widget creation: 201 Created
- Widget retrieval: 200 OK
- Widget update: 200 OK
- Invalid widget_type: 422 Unprocessable Entity
- Widget deletion: 204 No Content
- Deleted widget retrieval: 404 Not Found

### Tenant Isolation
- Tenant A authenticated request against Tenant B widget: 404 Not Found
- Confirms widget access is scoped by 	enant_id.

### Cross-Origin Widget
- Customer test site served from http://localhost:5500
- API served from http://localhost:8000
- Widget rendered successfully on the separate origin.
- Browser submission displayed: Thanks! Your submission was received.

### CORS and Preflight
- Cross-origin config request returned 200 OK.
- Access-Control-Allow-Origin: http://localhost:5500
- OPTIONS /submissions: 200 OK

### Honeypot Protection
- Submission with populated honeypot returned 200 OK / ccepted.
- Honeypot submission was not stored in the database.
- Widget includes a hidden website honeypot field.

### Rate Limiting
- IP rate limit configured at 5 requests per 60 seconds.
- Requests 1–5: 200 OK
- Request 6: 429 Too Many Requests

### Idempotency
- First request using the same Idempotency-Key: 200 OK, duplicate: false
- Second identical request: 200 OK, duplicate: true
- Both responses returned the same submission ID.
- Confirms duplicate lead creation is prevented.

### Notification Failure Isolation
- Notification enqueue was deliberately forced to raise an exception.
- Lead submission still returned 200 OK with status: accepted.
- Confirms notification side effects do not break lead submission.
- Temporary failure was removed and normal notification enqueue code restored.
