from psycopg.types.json import Jsonb
from uuid import UUID, uuid4



from app.db import get_connection
from app.services.geo import enrich_ip
from app.services.notifications import enqueue_notification


def create_submission(
    widget_id: UUID,
    data: dict,
    ip_address: str,
    idempotency_key: str | None,
):
    with get_connection() as connection:
        widget = connection.execute(
            """
            SELECT tenant_id
            FROM widgets
            WHERE id = %s
            """,
            (widget_id,),
        ).fetchone()

        if not widget:
            return None

        tenant_id = widget[0]

    if idempotency_key:
        with get_connection() as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM submissions
                WHERE widget_id = %s
                  AND idempotency_key = %s
                """,
                (widget_id, idempotency_key),
            ).fetchone()

        if existing:
            return {
                "id": existing[0],
                "duplicate": True,
            }

    geo = enrich_ip(ip_address)

    submission_id = uuid4()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO submissions (
                id,
                widget_id,
                tenant_id,
                data,
                ip_address,
                country,
                city,
                geo_provider,
                idempotency_key
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                submission_id,
                widget_id,
                tenant_id,
                Jsonb(data),
                ip_address,
                geo["country"],
                geo["city"],
                geo["provider"],
                idempotency_key,
            ),
        )

    try:
        enqueue_notification(submission_id)
    except Exception as exc:
        print(f"NOTIFICATION ENQUEUE ERROR: {type(exc).__name__}: {exc}")

    return {
        "id": submission_id,
        "duplicate": False,
        "country": geo["country"],
        "city": geo["city"],
        "provider": geo["provider"],
    }