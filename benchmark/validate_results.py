from __future__ import annotations

import csv

from .config import ROOT


def main() -> None:
    required = ("raw_results.csv","summary_results.csv","insert_results.csv","storage_results.csv")
    for name in required:
        path = ROOT / "results" / name
        if not path.exists(): raise SystemExit(f"Missing {path}; run benchmark.run_all first")
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if not rows: raise SystemExit(f"Empty result file: {path}")
        if any(str(r.get("is_real","")).lower() not in ("true","1") for r in rows): raise SystemExit(f"Non-real row detected in {path}")
    print("All result files are non-empty and explicitly marked as real measurements.")


if __name__ == "__main__": main()
