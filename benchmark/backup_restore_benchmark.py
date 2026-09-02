from __future__ import annotations

import csv
import subprocess
import time
from pathlib import Path

from .config import ROOT, Settings


def timed(database: str, operation: str, command: list[str], output: Path | None = None) -> dict:
    start = time.perf_counter()
    subprocess.run(command, cwd=ROOT, check=True)
    elapsed = time.perf_counter() - start
    return {"database":database,"operation":operation,"elapsed_seconds":elapsed,"backup_bytes":output.stat().st_size if output and output.exists() else "","is_real":True}


def main() -> None:
    s = Settings()
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)
    results = []
    sql_bak = backup_dir / "OnlineShopDB_sqlserver.bak"
    # SQL backup file is written inside the bind-mounted /var/opt/mssql/backup.
    results.append(timed("sqlserver","backup",["docker","compose","exec","-T","sqlserver","/opt/mssql-tools18/bin/sqlcmd","-S","localhost","-U",s.mssql_user,"-P",s.mssql_password,"-C","-Q","BACKUP DATABASE OnlineShopDB TO DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH INIT, COMPRESSION, CHECKSUM"] ,sql_bak))
    results.append(timed("sqlserver","restore",["docker","compose","exec","-T","sqlserver","/opt/mssql-tools18/bin/sqlcmd","-S","localhost","-U",s.mssql_user,"-P",s.mssql_password,"-C","-Q","IF DB_ID('OnlineShopDB_restore') IS NOT NULL BEGIN ALTER DATABASE OnlineShopDB_restore SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE OnlineShopDB_restore; END; RESTORE DATABASE OnlineShopDB_restore FROM DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH MOVE 'OnlineShopDB' TO '/var/opt/mssql/data/OnlineShopDB_restore.mdf', MOVE 'OnlineShopDB_log' TO '/var/opt/mssql/data/OnlineShopDB_restore_log.ldf', RECOVERY"] ))
    pg_bak = backup_dir / "OnlineShopDB_postgresql.dump"
    results.append(timed("postgresql","backup",["docker","compose","exec","-T","postgres","pg_dump","-U",s.postgres_user,"-Fc","-f","/backups/OnlineShopDB_postgresql.dump",s.postgres_database],pg_bak))
    results.append(timed("postgresql","restore",["docker","compose","exec","-T","postgres","bash","-lc",f"dropdb -U {s.postgres_user} --if-exists OnlineShopDB_restore && createdb -U {s.postgres_user} OnlineShopDB_restore && pg_restore -U {s.postgres_user} -d OnlineShopDB_restore /backups/OnlineShopDB_postgresql.dump"]))
    mongo_bak = backup_dir / "OnlineShopDB_mongodb.archive.gz"
    results.append(timed("mongodb","backup",["docker","compose","exec","-T","mongodb","mongodump","--username",s.mongo_user,"--password",s.mongo_password,"--authenticationDatabase","admin","--db",s.mongo_database,"--archive=/backups/OnlineShopDB_mongodb.archive.gz","--gzip"],mongo_bak))
    results.append(timed("mongodb","restore",["docker","compose","exec","-T","mongodb","mongorestore","--username",s.mongo_user,"--password",s.mongo_password,"--authenticationDatabase","admin","--archive=/backups/OnlineShopDB_mongodb.archive.gz","--gzip","--nsFrom=OnlineShopDB.*","--nsTo=OnlineShopDB_restore.*","--drop"]))
    path = ROOT / "results" / "backup_restore_results.csv"
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0])); writer.writeheader(); writer.writerows(results)
    print(path)


if __name__ == "__main__":
    main()
