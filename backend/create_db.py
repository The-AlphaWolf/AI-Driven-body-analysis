"""
Create the local development database if it does not already exist.

Only needed for local Postgres. Cloud providers (Neon, Render) hand you a
database that already exists — run `flask db upgrade` against it instead.

Credentials come from the environment; never hardcode them here.
"""
import os
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DEV_DB_NAME", "stylesense")


def main() -> int:
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        print(
            "POSTGRES_PASSWORD is not set. Add it to backend/.env "
            "(see .env.example) and re-run.",
            file=sys.stderr,
        )
        return 1

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=password,
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
    except psycopg2.Error as e:
        print(f"Could not connect to Postgres: {e}", file=sys.stderr)
        return 1

    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,)
            )
            if cursor.fetchone():
                print(f"Database '{DB_NAME}' already exists.")
            else:
                # Identifiers cannot be parameterised; DB_NAME is operator-supplied.
                cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
                print(f"Database '{DB_NAME}' created successfully.")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
