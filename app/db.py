from contextlib import contextmanager

import psycopg

from app.config import settings


@contextmanager
def get_connection():
    connection = psycopg.connect(settings.database_url)

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()