from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from app.db import get_connection


def create_widget(tenant_id: UUID, payload):
    widget_id = uuid4()

    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO widgets (
                id,
                tenant_id,
                widget_type,
                title,
                description,
                fields,
                button_text
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                tenant_id,
                widget_type,
                title,
                description,
                fields,
                button_text,
                created_at
            """,
            (
                widget_id,
                tenant_id,
                payload.widget_type,
                payload.title,
                payload.description,
                Jsonb(payload.fields),
                payload.button_text,
            ),
        ).fetchone()

    return row[0]


def get_widget(tenant_id: UUID, widget_id: UUID):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                tenant_id,
                widget_type,
                title,
                description,
                fields,
                button_text,
                created_at
            FROM widgets
            WHERE id = %s
              AND tenant_id = %s
            """,
            (widget_id, tenant_id),
        ).fetchone()
def update_widget(tenant_id: UUID, widget_id: UUID, payload):
    update_fields = payload.model_dump(exclude_unset=True)

    if not update_fields:
        return get_widget(tenant_id, widget_id)

    allowed_fields = {
        "widget_type",
        "title",
        "description",
        "fields",
        "button_text",
        "display_options",
    }

    update_fields = {
        key: value
        for key, value in update_fields.items()
        if key in allowed_fields
    }

    set_clauses = []
    values = []

    for key, value in update_fields.items():
        if key == "display_options":
            set_clauses.append(f"{key} = %s")
            values.append(Jsonb(value))
        elif key == "fields":
            set_clauses.append(f"{key} = %s")
            values.append(Jsonb(value))
        else:
            set_clauses.append(f"{key} = %s")
            values.append(value)

    values.extend([widget_id, tenant_id])

    with get_connection() as connection:
        row = connection.execute(
            f"""
            UPDATE widgets
            SET {", ".join(set_clauses)}
            WHERE id = %s
              AND tenant_id = %s
            RETURNING
                id,
                tenant_id,
                widget_type,
                title,
                description,
                fields,
                button_text,
                created_at
            """,
            values,
        ).fetchone()

    return row

def get_public_widget(widget_id: UUID):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                tenant_id,
                widget_type,
                title,
                description,
                fields,
                button_text,
                created_at
            FROM widgets
            WHERE id = %s
            """,
            (widget_id,),
        ).fetchone()


def delete_widget(tenant_id: UUID, widget_id: UUID):
    with get_connection() as connection:
        result = connection.execute(
            """
            DELETE FROM widgets
            WHERE id = %s
              AND tenant_id = %s
            """,
            (widget_id, tenant_id),
        )

    return result.rowcount