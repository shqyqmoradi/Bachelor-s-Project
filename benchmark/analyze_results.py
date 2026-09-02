from __future__ import annotations

import pandas as pd

from .config import ROOT


def fmt(value: float, unit: str) -> str:
    return f"{value:,.3f} {unit}"


def main() -> None:
    results = ROOT / "results"
    required = [results / n for n in ("raw_results.csv","summary_results.csv","insert_results.csv","storage_results.csv")]
    if any(not p.exists() for p in required):
        raise SystemExit("Run benchmark.run_all before generating measured analysis.")
    raw = pd.read_csv(required[0])
    summary = pd.read_csv(required[1])
    inserts = pd.read_csv(required[2])
    storage = pd.read_csv(required[3])
    indexed = summary[summary.index_phase == "with_indexes"]
    overall = indexed.groupby("database",as_index=False).average_ms.mean().sort_values("average_ms")
    dbs = [db for db in ("sqlserver","postgresql","mongodb") if db in set(overall.database)]
    indexed_raw = raw[raw.index_phase == "with_indexes"]
    backup_path = results / "backup_restore_results.csv"
    backups = pd.read_csv(backup_path) if backup_path.exists() else pd.DataFrame()
    metric_rows = []
    def add_metric(metric, getter):
        row = {"metric":metric}
        row.update({db:getter(db) for db in dbs})
        metric_rows.append(row)
    add_metric("Insert Time (s)", lambda db: float(inserts.loc[inserts.database==db,"elapsed_seconds"].iloc[0]))
    add_metric("Average Query Time (ms)", lambda db: float(indexed_raw.loc[indexed_raw.database==db,"elapsed_ms"].mean()))
    add_metric("Minimum Query Time (ms)", lambda db: float(indexed_raw.loc[indexed_raw.database==db,"elapsed_ms"].min()))
    add_metric("Maximum Query Time (ms)", lambda db: float(indexed_raw.loc[indexed_raw.database==db,"elapsed_ms"].max()))
    add_metric("Average CPU (%)", lambda db: float(indexed_raw.loc[indexed_raw.database==db,"avg_cpu_percent"].mean()))
    add_metric("Peak Host RAM (MiB)", lambda db: float(indexed_raw.loc[indexed_raw.database==db,"peak_ram_mb"].max()))
    add_metric("Total Storage (MiB)", lambda db: float(storage.loc[storage.database==db,"total_bytes"].iloc[0]) / 2**20)
    if not backups.empty:
        add_metric("Backup Time (s)", lambda db: float(backups.loc[(backups.database==db)&(backups.operation=="backup"),"elapsed_seconds"].iloc[0]))
        add_metric("Restore Time (s)", lambda db: float(backups.loc[(backups.database==db)&(backups.operation=="restore"),"elapsed_seconds"].iloc[0]))
    comparison = pd.DataFrame(metric_rows)
    comparison.to_csv(results / "final_comparison.csv", index=False)
    query_pivot = indexed.pivot(index="query_id",columns="database",values="average_ms").reset_index()
    lines = ["# نتایج اندازه‌گیری‌شده", "", "> این فایل فقط از CSVهای دارای `is_real=true` تولید شده است.", "", "## جدول نهایی معیارهای عددی", "", comparison.to_markdown(index=False, floatfmt=".3f"), "", "Developer Effort با rubric و diary امتیاز می‌گیرد و Security یک feature matrix است؛ تبدیل این دو به عدد بدون ارزیابی ثبت‌شده انجام نمی‌شود.", "", "## میانگین هر Query در فاز indexed", "", query_pivot.to_markdown(index=False,floatfmt=".3f"), "", "## برندهٔ مشاهده‌شده برای هر Query در فاز indexed", "", "| Query | کمترین Average | زمان (ms) |", "|---|---|---:|"]
    for qid, group in indexed.groupby("query_id"):
        best = group.sort_values("average_ms").iloc[0]
        lines.append(f"| {qid} | {best.database} | {best.average_ms:.3f} |")
    lines += ["", "این جدول علیت را ثابت نمی‌کند. برای توضیح تفاوت‌ها باید execution plan، تعداد اسناد/ردیف‌های بررسی‌شده، cache، serialization و overhead اتصال همراه نتایج بررسی شوند. Q05 و Q13 به‌علت تفاوت embedding/JOIN کاملاً هم‌ساخت نیستند."]
    out = ROOT / "report" / "measured_results.md"
    out.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(out)


if __name__ == "__main__": main()
