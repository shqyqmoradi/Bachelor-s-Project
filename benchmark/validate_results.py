from __future__ import annotations

import csv
import json

from .config import ROOT


def main() -> None:
    required = ("raw_results.csv","summary_results.csv","insert_results.csv","storage_results.csv")
    loaded: dict[str, list[dict]] = {}
    for name in required:
        path = ROOT / "results" / name
        if not path.exists():
            raise SystemExit(f"Missing {path}; run benchmark.run_all first")
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if not rows:
            raise SystemExit(f"Empty result file: {path}")
        if any(str(r.get("is_real", "")).lower() not in ("true", "1") for r in rows):
            raise SystemExit(f"Non-real row detected in {path}")
        loaded[name] = rows

    raw = loaded["raw_results.csv"]
    databases = {row["database"] for row in raw}
    phases = {row["index_phase"] for row in raw}
    operations = {row["query_id"] for row in raw}
    metadata = json.loads((ROOT / "results" / "environment.json").read_text(encoding="utf-8"))
    repetitions = int(metadata["repetitions"])
    expected_rows = len(databases) * len(phases) * len(operations) * repetitions
    if len(operations) != 16 or len(raw) != expected_rows:
        raise SystemExit(
            f"Raw measurement mismatch: rows={len(raw)}, operations={len(operations)}, "
            f"expected_rows={expected_rows}"
        )

    restore_path = ROOT / "results" / "restore_validation.csv"
    if restore_path.exists():
        restore_rows = list(csv.DictReader(restore_path.open(encoding="utf-8")))
        expected_entities = {
            "customers", "addresses", "categories", "products",
            "orders", "order_items", "payments", "shipment",
        }
        for database in databases:
            actual = {row["entity"] for row in restore_rows if row["database"] == database}
            if actual != expected_entities:
                raise SystemExit(
                    f"Restore validation mismatch for {database}: "
                    f"missing={sorted(expected_entities - actual)}, extra={sorted(actual - expected_entities)}"
                )

    print(
        f"Validated {len(raw)} real measurements across {len(operations)} operations "
        "and restore counts for all eight entities."
    )


if __name__ == "__main__":
    main()
