"""Connection settings and a small transaction helper; no ORM is hidden here."""

import os
from contextlib import contextmanager
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

from .errors import InventoryError

PROJECT_DIR = Path(__file__).resolve().parent.parent


def settings():
    # Resolve .env relative to the project, regardless of the current directory.
    # Existing environment variables take priority over values in .env.
    load_dotenv(PROJECT_DIR / ".env")
    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError:
        raise InventoryError("MYSQL_PORT must be a whole number.") from None
    if not 1 <= port <= 65535:
        raise InventoryError("MYSQL_PORT must be between 1 and 65535.")
    password = os.getenv("MYSQL_PASSWORD")
    if not password:
        raise InventoryError("Set MYSQL_PASSWORD in .env before connecting.")
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": port,
        "database": os.getenv("MYSQL_DATABASE", "inventory_management"),
        "user": os.getenv("MYSQL_USER", "portfolio"),
        "password": password,
        "charset": "utf8mb4",
        "connection_timeout": 10,
        "autocommit": False,
    }


class Database:
    def __init__(self, connection_settings=None):
        self.connection_settings = connection_settings

    def connect(self):
        return mysql.connector.connect(**(self.connection_settings or settings()))

    @contextmanager
    def transaction(self):
        connection = self.connect()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def initialize(self):
        # schema.sql is a trusted, local file with simple CREATE TABLE statements.
        # MySQL DDL commits implicitly; this is not a schema-migration system.
        with self.transaction() as cursor:
            for statement in (PROJECT_DIR / "schema.sql").read_text(encoding="utf-8").split(";"):
                if statement.strip():
                    cursor.execute(statement)
