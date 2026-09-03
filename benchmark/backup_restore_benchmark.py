from __future__ import annotations

import csv
import subprocess
import time
from contextlib import closing
from pathlib import Path

from .config import ROOT, Settings
from .db import mongo_connect, postgres_connect, sqlserver_connect


RELATIONAL_ENTITIES = (
    ("customers", "Customers", "customers"),
    ("addresses", "Addresses", "addresses"),
    ("categories", "Categories", "categories"),
    ("products", "Products", "products"),
    ("orders", "Orders", "orders"),
    ("order_items", "OrderItems", "order_items"),
    ("payments", "Payments", "payments"),
    ("shipment", "Shipment", "shipment"),
)


def timed(
    database: str,
    operation: str,
    command: list[str],
    output: Path | None = None,
) -> dict:
    start = time.perf_counter()
    subprocess.run(command, cwd=ROOT, check=True)
    elapsed = time.perf_counter() - start
    return {
        "database": database,
        "operation": operation,
        "elapsed_seconds": elapsed,
        "backup_bytes": output.stat().st_size if output and output.exists() else "",
        "is_real": True,
    }


def validation_row(database: str, entity: str, count: int, method: str) -> dict:
    return {
        "database": database,
        "restore_database": "OnlineShopDB_restore",
        "entity": entity,
        "count": count,
        "verification_method": method,
        "is_real": True,
    }


def validate_sqlserver_restore(s: Settings) -> list[dict]:
    rows = []
    with closing(sqlserver_connect(s, "OnlineShopDB_restore")) as connection:
        cursor = connection.cursor()
        for entity, sqlserver_table, _ in RELATIONAL_ENTITIES:
            count = int(cursor.execute(f"SELECT COUNT_BIG(*) FROM dbo.{sqlserver_table}").fetchone()[0])
            rows.append(validation_row("sqlserver", entity, count, "direct_count_query"))
    return rows


def validate_postgresql_restore(s: Settings) -> list[dict]:
    rows = []
    with postgres_connect(s, "OnlineShopDB_restore") as connection:
        with connection.cursor() as cursor:
            for entity, _, postgresql_table in RELATIONAL_ENTITIES:
                count = int(cursor.execute(f"SELECT COUNT(*) FROM {postgresql_table}").fetchone()[0])
                rows.append(validation_row("postgresql", entity, count, "direct_count_query"))
    return rows


def aggregate_count(collection, pipeline: list[dict]) -> int:
    result = next(collection.aggregate([*pipeline, {"$count": "count"}]), None)
    return int(result["count"]) if result else 0


def validate_mongodb_restore(s: Settings) -> list[dict]:
    with mongo_connect(s) as client:
        database = client["OnlineShopDB_restore"]
        counts = (
            ("customers", database.customers.count_documents({}), "direct_document_count"),
            ("addresses", aggregate_count(database.customers, [{"$unwind": "$addresses"}]), "embedded_address_count"),
            ("categories", database.categories.count_documents({}), "direct_document_count"),
            ("products", database.products.count_documents({}), "direct_document_count"),
            ("orders", database.orders.count_documents({}), "direct_document_count"),
            ("order_items", aggregate_count(database.orders, [{"$unwind": "$items"}]), "embedded_item_count"),
            ("payments", database.orders.count_documents({"payment": {"$type": "object"}}), "embedded_payment_count"),
            ("shipment", database.orders.count_documents({"shipment": {"$type": "object"}}), "embedded_shipment_count"),
        )
        return [validation_row("mongodb", entity, int(count), method) for entity, count, method in counts]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    s = Settings()
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)
    results = []
    validations = []

    sql_bak = backup_dir / "OnlineShopDB_sqlserver.bak"
    results.append(
        timed(
            "sqlserver",
            "backup",
            [
                "docker", "compose", "exec", "-T", "sqlserver",
                "/opt/mssql-tools18/bin/sqlcmd", "-S", "localhost", "-U", s.mssql_user,
                "-P", s.mssql_password, "-C", "-Q",
                "BACKUP DATABASE OnlineShopDB TO DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH INIT, COMPRESSION, CHECKSUM",
            ],
            sql_bak,
        )
    )
    results.append(
        timed(
            "sqlserver",
            "restore",
            [
                "docker", "compose", "exec", "-T", "sqlserver",
                "/opt/mssql-tools18/bin/sqlcmd", "-S", "localhost", "-U", s.mssql_user,
                "-P", s.mssql_password, "-C", "-Q",
                "IF DB_ID('OnlineShopDB_restore') IS NOT NULL BEGIN ALTER DATABASE OnlineShopDB_restore SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE OnlineShopDB_restore; END; RESTORE DATABASE OnlineShopDB_restore FROM DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH MOVE 'OnlineShopDB' TO '/var/opt/mssql/data/OnlineShopDB_restore.mdf', MOVE 'OnlineShopDB_log' TO '/var/opt/mssql/data/OnlineShopDB_restore_log.ldf', RECOVERY",
            ],
        )
    )
    validations.extend(validate_sqlserver_restore(s))

    pg_bak = backup_dir / "OnlineShopDB_postgresql.dump"
    results.append(
        timed(
            "postgresql",
            "backup",
            [
                "docker", "compose", "exec", "-T", "postgres", "pg_dump",
                "-U", s.postgres_user, "-Fc", "-f", "/backups/OnlineShopDB_postgresql.dump",
                s.postgres_database,
            ],
            pg_bak,
        )
    )
    results.append(
        timed(
            "postgresql",
            "restore",
            [
                "docker", "compose", "exec", "-T", "postgres", "bash", "-lc",
                f"dropdb -U {s.postgres_user} --if-exists OnlineShopDB_restore && createdb -U {s.postgres_user} OnlineShopDB_restore && pg_restore -U {s.postgres_user} -d OnlineShopDB_restore /backups/OnlineShopDB_postgresql.dump",
            ],
        )
    )
    validations.extend(validate_postgresql_restore(s))

    mongo_bak = backup_dir / "OnlineShopDB_mongodb.archive.gz"
    results.append(
        timed(
            "mongodb",
            "backup",
            [
                "docker", "compose", "exec", "-T", "mongodb", "mongodump",
                "--username", s.mongo_user, "--password", s.mongo_password,
                "--authenticationDatabase", "admin", "--db", s.mongo_database,
                "--archive=/backups/OnlineShopDB_mongodb.archive.gz", "--gzip",
            ],
            mongo_bak,
        )
    )
    results.append(
        timed(
            "mongodb",
            "restore",
            [
                "docker", "compose", "exec", "-T", "mongodb", "mongorestore",
                "--username", s.mongo_user, "--password", s.mongo_password,
                "--authenticationDatabase", "admin",
                "--archive=/backups/OnlineShopDB_mongodb.archive.gz", "--gzip",
                "--nsFrom=OnlineShopDB.*", "--nsTo=OnlineShopDB_restore.*", "--drop",
            ],
        )
    )
    validations.extend(validate_mongodb_restore(s))

    results_dir = ROOT / "results"
    write_csv(results_dir / "backup_restore_results.csv", results)
    write_csv(results_dir / "restore_validation.csv", validations)
    print(results_dir / "backup_restore_results.csv")
    print(results_dir / "restore_validation.csv")


if __name__ == "__main__":
    main()
