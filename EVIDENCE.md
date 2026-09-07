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