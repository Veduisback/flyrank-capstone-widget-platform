from psycopg.types.json import Jsonb
from uuid import uuid4

from app.auth import hash_password
from app.db import get_connection


def main():
    tenant_a = uuid4()
    tenant_b = uuid4()

    user_a = uuid4()
    user_b = uuid4()

    widget_a = uuid4()
    widget_b = uuid4()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tenants (id, name)
            VALUES (%s, %s), (%s, %s)
            """,
            (
                tenant_a,
                "Demo Company A",
                tenant_b,
                "Demo Company B",
            ),
        )

        connection.execute(
            """
            INSERT INTO users (
                id,
                tenant_id,
                email,
                password_hash
            )
            VALUES (%s, %s, %s, %s),
                   (%s, %s, %s, %s)
            """,
            (
                user_a,
                tenant_a,
                "owner-a@example.com",
                hash_password("Password123!"),
                user_b,
                tenant_b,
                "owner-b@example.com",
                hash_password("Password123!"),
            ),
        )

        connection.execute(
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
            VALUES (
                %s,
                %s,
                'signup',
                'Get a Free Quote',
                'Leave your details and we will contact you.',
                %s,
                'Send Request'
            ),
            (
                %s,
                %s,
                'contact',
                'Contact Us',
                'Send us a message.',
                %s,
                'Send Message'
            )
            """,
            (
                widget_a,
                tenant_a,
                Jsonb(["name", "email", "phone"]),
                widget_b,
                tenant_b,
                Jsonb(["name", "email", "message"]),
            ),
        )

    print("Seed complete")
    print("Tenant A user: owner-a@example.com")
    print("Tenant B user: owner-b@example.com")
    print("Password: Password123!")
    print(f"Widget A: {widget_a}")
    print(f"Widget B: {widget_b}")


if __name__ == "__main__":
    main()