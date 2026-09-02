from __future__ import annotations

import argparse
import re
import subprocess
from contextlib import closing

from .config import ROOT, Settings
from .db import execute_postgres_file, postgres_connect, sqlserver_connect


def setup_sqlserver(s: Settings) -> None:
    # CREATE DATABASE must execute outside a user transaction.
    with closing(sqlserver_connect(s, "master", autocommit=True)) as connection:
        connection.cursor().execute("IF DB_ID(N'OnlineShopDB') IS NULL CREATE DATABASE OnlineShopDB")
    script = (ROOT / "sqlserver" / "schema.sql").read_text(encoding="utf-8")
    batches = re.split(r"^\s*GO\s*$", script, flags=re.MULTILINE | re.IGNORECASE)
    with closing(sqlserver_connect(s)) as connection:
        for batch in batches:
            upper = batch.upper().strip()
            if not upper or "CREATE DATABASE" in upper or upper.startswith("USE "):
                continue
            connection.cursor().execute(batch)
        connection.commit()


def setup_postgresql(s: Settings) -> None:
    with postgres_connect(s) as connection:
        execute_postgres_file(connection, ROOT / "postgresql" / "schema.sql")


def setup_mongodb(s: Settings) -> None:
    script = (ROOT / "mongodb" / "schema.js").read_text(encoding="utf-8")
    command = ["docker", "compose", "exec", "-T", "mongodb", "mongosh", "--quiet", "--username", s.mongo_user, "--password", s.mongo_password, "--authenticationDatabase", "admin"]
    subprocess.run(command, cwd=ROOT, input=script, text=True, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", choices=("all", "sqlserver", "postgresql", "mongodb"), default="all")
    args = parser.parse_args()
    s = Settings()
    actions = {"sqlserver": setup_sqlserver, "postgresql": setup_postgresql, "mongodb": setup_mongodb}
    for name, action in actions.items():
        if args.database in ("all", name):
            print(f"Setting up {name}...")
            action(s)


if __name__ == "__main__":
    main()
