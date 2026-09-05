from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

from .config import ROOT


DATASET_DESCRIPTION = (
    "100000 orders, 20000 customers, 20000 addresses, 10000 products, "
    "50 categories; seed 20260830"
)


def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = ROOT / "results" / "by_database"
    databases = ("sqlserver", "postgresql", "mongodb")
    combined = {}
    for name in (
        "raw_results.csv",
        "summary_results.csv",
        "insert_results.csv",
        "storage_results.csv",
    ):
        rows = []
        for db in databases:
            rows.extend(read_csv(base / db / name))
        write_csv(ROOT / "results" / name, rows)
        combined[name] = rows
    backups = []
    for db in databases:
        backups.extend(read_csv(base / db / "backup_restore_results.csv"))
    write_csv(ROOT / "results" / "backup_restore_results.csv", backups)
    metadata = {
        "merged_utc": datetime.now(timezone.utc).isoformat(),
        "databases": databases,
        "dataset": DATASET_DESCRIPTION,
        "repetitions": 10,
        "index_phases": ["without_extra_indexes", "with_indexes"],
        "cache_mode": "warm",
        "host_architecture": "arm64; SQL Server linux/amd64 emulation (interpret as an environment limitation)",
        "docker_memory_bytes": 4106604544,
        "sources": "results/by_database/*",
    }
    (ROOT / "results" / "environment.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    (ROOT / "results" / "results.json").write_text(
        json.dumps(
            {"metadata": metadata, **combined, "backup_restore": backups}, indent=2
        ),
        encoding="utf-8",
    )
    print(
        f"Merged {len(combined['raw_results.csv'])} raw query rows and {len(backups)} backup rows."
    )


if __name__ == "__main__":
    main()
