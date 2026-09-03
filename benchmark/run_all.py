from __future__ import annotations

import argparse
import csv
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import psutil

from .benchmark_runner import configure_indexes, mongodb_benchmark, relational_benchmark, storage_and_version, summarize
from .charts import generate as generate_charts
from .config import ROOT, Settings
from .data_generator import CanonicalGenerator
from .load_data import load_mongodb, load_postgresql, load_sqlserver
from .setup_databases import setup_mongodb, setup_postgresql, setup_sqlserver


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end, sequential and reproducible benchmark.")
    parser.add_argument("--orders", type=int, help="Canonical order count (10k/100k/500k/1m).")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--database", choices=("all","sqlserver","postgresql","mongodb"), default="all")
    parser.add_argument("--skip-load", action="store_true", help="Reuse an already loaded canonical dataset.")
    parser.add_argument("--skip-charts", action="store_true")
    args = parser.parse_args()
    defaults = Settings()
    s = Settings(orders=args.orders or defaults.orders, repetitions=args.repetitions or defaults.repetitions)
    selected = [d for d in ("sqlserver","postgresql","mongodb") if args.database in ("all",d)]
    setup = {"sqlserver":setup_sqlserver,"postgresql":setup_postgresql,"mongodb":setup_mongodb}
    loaders = {"sqlserver":load_sqlserver,"postgresql":load_postgresql,"mongodb":load_mongodb}
    raw, inserts, storage = [], [], []
    public_settings = {"seed":s.seed,"orders":s.orders,"repetitions":s.repetitions,"batch_size":s.batch_size,"customer_count":s.customer_count,"address_count":s.customer_count,"product_count":s.product_count,"category_count":s.category_count}
    metadata = {"started_utc":datetime.now(timezone.utc).isoformat(),"os":platform.platform(),"python":platform.python_version(),"physical_cores":psutil.cpu_count(logical=False),"logical_cores":psutil.cpu_count(),"ram_bytes":psutil.virtual_memory().total,"settings":public_settings,"cache_policy":"warm; one untimed warm-up then timed repetitions","cold_cache":"not automated because portable, equivalent cache eviction is unavailable"}
    for database in selected:
        print(f"=== {database} ===")
        if not args.skip_load:
            setup[database](s)
            inserts.append(loaders[database](s, CanonicalGenerator(s)))
        configure_indexes(database, s, False)
        raw.extend(mongodb_benchmark("without_extra_indexes",s) if database=="mongodb" else relational_benchmark(database,"without_extra_indexes",s))
        configure_indexes(database, s, True)
        raw.extend(mongodb_benchmark("with_indexes",s) if database=="mongodb" else relational_benchmark(database,"with_indexes",s))
        storage.append(storage_and_version(database,s))
        # Per-database checkpoint: a later storage/plotting failure never loses timed rows.
        checkpoint = output = ROOT / "results" / "by_database" / database
        checkpoint.mkdir(parents=True, exist_ok=True)
        write_csv(checkpoint / "raw_results.csv", [r for r in raw if r["database"] == database])
        write_csv(checkpoint / "summary_results.csv", summarize([r for r in raw if r["database"] == database]))
        write_csv(checkpoint / "insert_results.csv", [r for r in inserts if r["database"] == database])
        write_csv(checkpoint / "storage_results.csv", [r for r in storage if r["database"] == database])
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    summary = summarize(raw)
    write_csv(output / "raw_results.csv", raw)
    write_csv(output / "summary_results.csv", summary)
    write_csv(output / "insert_results.csv", inserts)
    write_csv(output / "storage_results.csv", storage)
    (output / "results.json").write_text(json.dumps({"metadata":metadata,"insert":inserts,"storage":storage,"raw":raw,"summary":summary}, indent=2, default=str), encoding="utf-8")
    (output / "environment.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    if not args.skip_charts:
        generate_charts()
    print(f"Real results written under {output}")


if __name__ == "__main__":
    main()
