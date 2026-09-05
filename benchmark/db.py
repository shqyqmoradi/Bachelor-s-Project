from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Sequence

import pyodbc
import psycopg
from pymongo import MongoClient

from .config import Settings


def sqlserver_connect(
    s: Settings, database: str | None = None, autocommit: bool = False
) -> pyodbc.Connection:
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={s.mssql_host},{s.mssql_port};"
        f"DATABASE={database or s.mssql_database};UID={s.mssql_user};PWD={s.mssql_password};"
        "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=10",
        autocommit=autocommit,
    )


def postgres_connect(s: Settings, database: str | None = None) -> psycopg.Connection:
    return psycopg.connect(
        host=s.postgres_host,
        port=s.postgres_port,
        user=s.postgres_user,
        password=s.postgres_password,
        dbname=database or s.postgres_database,
        autocommit=False,
    )


def mongo_connect(s: Settings) -> MongoClient:
    return MongoClient(s.mongo_uri, serverSelectionTimeoutMS=10_000)


def execute_tsql_file(connection: pyodbc.Connection, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for batch in re.split(r"^\s*GO\s*$", text, flags=re.MULTILINE | re.IGNORECASE):
        if batch.strip():
            connection.cursor().execute(batch)
    connection.commit()


def execute_postgres_file(connection: psycopg.Connection, path: Path) -> None:
    connection.execute(path.read_text(encoding="utf-8"))
    connection.commit()


def sqlserver_many(
    connection: pyodbc.Connection, sql: str, rows: Sequence[tuple]
) -> None:
    if not rows:
        return
    cursor = connection.cursor()
    cursor.fast_executemany = True
    cursor.executemany(sql, rows)


def postgres_many(
    connection: psycopg.Connection, sql: str, rows: Sequence[tuple]
) -> None:
    if rows:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)


def fetch_all(cursor: Any) -> list[Any]:
    return list(cursor.fetchall()) if cursor.description else []
