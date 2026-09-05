from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import ROOT


def bar_chart(
    frame: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    title: str,
    output: Path,
    *,
    log_scale: bool = False,
) -> None:
    pivot = frame.pivot_table(index=x, columns=hue, values=y, aggfunc="mean")
    ax = pivot.plot(kind="bar", figsize=(13, 6))
    ax.set_title(title)
    if log_scale:
        ax.set_yscale("log")
        ax.set_ylabel(f"{y} (log scale)")
    else:
        ax.set_ylabel(y)
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def generate() -> list[Path]:
    raw_path, summary_path = (
        ROOT / "results" / "raw_results.csv",
        ROOT / "results" / "summary_results.csv",
    )
    if not raw_path.exists() or not summary_path.exists():
        print("Required result files are missing; run the benchmark first.")
        return []
    raw, summary = pd.read_csv(raw_path), pd.read_csv(summary_path)
    if raw.empty or not raw["is_real"].all():
        raise ValueError("Result data is empty or failed validation.")
    out = ROOT / "charts"
    paths = []
    specs = [
        (
            summary,
            "query_id",
            "average_ms",
            "database",
            "Warm-cache query performance (log scale)",
            out / "query_performance.png",
            True,
        ),
        (
            raw,
            "database",
            "avg_cpu_percent",
            "index_phase",
            "Average system CPU during queries",
            out / "cpu_usage.png",
            False,
        ),
        (
            raw,
            "database",
            "peak_ram_mb",
            "index_phase",
            "Peak host RAM during queries",
            out / "ram_usage.png",
            False,
        ),
    ]
    insert_path = ROOT / "results" / "insert_results.csv"
    if insert_path.exists():
        inserts = pd.read_csv(insert_path)
        inserts["series"] = "canonical load"
        specs.append(
            (
                inserts,
                "database",
                "elapsed_seconds",
                "series",
                "Canonical dataset insert performance",
                out / "insert_performance.png",
                False,
            )
        )
    for frame, x, y, hue, title, output, log_scale in specs:
        bar_chart(frame, x, y, hue, title, output, log_scale=log_scale)
        paths.append(output)
    storage_path = ROOT / "results" / "storage_results.csv"
    if storage_path.exists():
        storage = pd.read_csv(storage_path)
        melted = storage.melt(
            id_vars="database",
            value_vars=["data_bytes", "index_bytes", "total_bytes"],
            var_name="kind",
            value_name="bytes",
        )
        bar_chart(
            melted,
            "database",
            "bytes",
            "kind",
            "Database storage size",
            out / "storage_size.png",
        )
        paths.append(out / "storage_size.png")
    backup_path = ROOT / "results" / "backup_restore_results.csv"
    if backup_path.exists():
        backup = pd.read_csv(backup_path)
        bar_chart(
            backup,
            "database",
            "elapsed_seconds",
            "operation",
            "Backup and restore time",
            out / "backup_restore.png",
        )
        paths.append(out / "backup_restore.png")
    return paths


if __name__ == "__main__":
    print("\n".join(map(str, generate())))
