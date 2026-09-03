# Benchmark results

This directory contains the real 100,000-order benchmark measurements. The
`raw_results.csv` file has 960 rows: 3 databases x 2 index phases x 16 operations
x 10 repetitions. `summary_results.csv`, `insert_results.csv`,
`storage_results.csv`, `backup_restore_results.csv`, and
`restore_validation.csv` contain the derived and operational results.

Run `python -m benchmark.run_all` to regenerate the benchmark data,
`python -m benchmark.backup_restore_benchmark` to regenerate backup/restore and
restore-validation results, and `python -m benchmark.analyze_results` to rebuild
the final comparison and measured report section.
