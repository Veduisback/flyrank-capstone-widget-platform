import logging
import time
from uuid import UUID, uuid4

from app.config import settings
from app.db import get_connection


logger = logging.getLogger("notifications")


def enqueue_notification(submission_id: UUID):
    job_id = uuid4()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO notification_jobs (
                id,
                submission_id
            )
            VALUES (%s, %s)
            """,
            (job_id, submission_id),
        )


def process_pending_jobs():
    if not settings.notification_enabled:
        return

    with get_connection() as connection:
        jobs = connection.execute(
            """
            SELECT id, submission_id, attempts
            FROM notification_jobs
            WHERE status = 'pending'
            ORDER BY created_at
            LIMIT 10
            """
        ).fetchall()

    for job_id, submission_id, attempts in jobs:
        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE notification_jobs
                    SET attempts = attempts + 1
                    WHERE id = %s
                    """,
                    (job_id,),
                )

            # Simulated email/webhook side effect.
            print(
                f"NOTIFICATION: submission {submission_id} "
                "would trigger an email/webhook"
            )

            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE notification_jobs
                    SET status = 'completed',
                        processed_at = NOW()
                    WHERE id = %s
                    """,
                    (job_id,),
                )

        except Exception as exc:
            attempts += 1

            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE notification_jobs
                    SET status = CASE
                            WHEN attempts >= 3
                            THEN 'failed'
                            ELSE 'pending'
                        END,
                        last_error = %s
                    WHERE id = %s
                    """,
                    (str(exc), job_id),
                )

            if attempts >= 3:
                logger.error(
                    "Notification permanently failed: %s",
                    submission_id,
                )

            time.sleep(0.1)


