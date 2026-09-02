# Benchmark results

This directory intentionally contains no fabricated measurements. Running
`python -m benchmark.run_all` creates `raw_results.csv`, `summary_results.csv`,
`insert_results.csv`, `storage_results.csv`, `results.json`, and
`environment.json`. Backup/restore measurements are created separately by
`python -m benchmark.backup_restore_benchmark`. After those runs,
`python -m benchmark.analyze_results` creates `final_comparison.csv` and the
measured report section. Until then this directory remains intentionally empty.
