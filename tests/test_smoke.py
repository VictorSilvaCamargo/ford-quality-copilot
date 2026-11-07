"""Smoke tests for PostgreSQL connection and pgvector extension availability."""

from __future__ import annotations

import os

import psycopg
from dotenv import load_dotenv


def _build_conninfo() -> str:
    load_dotenv(override=False)
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "ford_quality")
    user = os.getenv("POSTGRES_USER", "ford_copilot")
    password = os.getenv("POSTGRES_PASSWORD", "ford_copilot_local_pw")
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def test_postgres_connection() -> None:
    """Verify that the application can connect to PostgreSQL and execute a query."""
    conninfo = _build_conninfo()
    with psycopg.connect(conninfo, connect_timeout=5) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1;")
        row = cur.fetchone()
        assert row == (1,)


def test_pgvector_extension_enabled() -> None:
    """Verify that the pgvector extension ('vector') is installed and operational."""
    conninfo = _build_conninfo()
    with psycopg.connect(conninfo, connect_timeout=5) as conn, conn.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ext_row = cur.fetchone()
        assert ext_row is not None, "Extension 'vector' is not enabled in PostgreSQL."
        assert ext_row[0] == "vector"

        cur.execute("SELECT '[1,2,3]'::vector <-> '[1,2,3]'::vector;")
        distance_row = cur.fetchone()
        assert distance_row is not None
        assert float(distance_row[0]) == 0.0
