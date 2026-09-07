from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.db import get_connection


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get("/submissions")
def submissions(
    current_user=Depends(get_current_user),
):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                widget_id,
                data,
                country,
                city,
                geo_provider,
                created_at
            FROM submissions
            WHERE tenant_id = %s
            ORDER BY created_at DESC
            LIMIT 100
            """,
            (current_user["tenant_id"],),
        ).fetchall()

    return [
        {
            "id": row[0],
            "widget_id": row[1],
            "data": row[2],
            "country": row[3],
            "city": row[4],
            "geo_provider": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


@router.get("/stats")
def stats(
    current_user=Depends(get_current_user),
):
    with get_connection() as connection:
        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM submissions
            WHERE tenant_id = %s
            """,
            (current_user["tenant_id"],),
        ).fetchone()[0]

        by_widget = connection.execute(
            """
            SELECT widget_id, COUNT(*)
            FROM submissions
            WHERE tenant_id = %s
            GROUP BY widget_id
            ORDER BY COUNT(*) DESC
            """,
            (current_user["tenant_id"],),
        ).fetchall()

        by_country = connection.execute(
            """
            SELECT country, COUNT(*)
            FROM submissions
            WHERE tenant_id = %s
              AND country IS NOT NULL
            GROUP BY country
            ORDER BY COUNT(*) DESC
            """,
            (current_user["tenant_id"],),
        ).fetchall()

    return {
        "total_submissions": total,
        "per_widget": [
            {
                "widget_id": row[0],
                "count": row[1],
            }
            for row in by_widget
        ],
        "geo": [
            {
                "country": row[0],
                "count": row[1],
            }
            for row in by_country
        ],
    }