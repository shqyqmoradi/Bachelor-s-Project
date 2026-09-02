# Project execution plan

## Phase 1 — controlled design

1. Freeze logical entities, cardinalities, constraints and money/time semantics.
2. Normalize SQL Server/PostgreSQL; choose bounded ownership-based embedding for MongoDB.
3. Pre-register scale, seed, repetitions, index phases and warm-cache policy.

Deliverables: `report/erd.md`, three schema files, methodology in `report/report.md`.

## Phase 2 — reproducible infrastructure

1. Start pinned containers with equal 2-CPU/4-GiB limits and isolated volumes.
2. Record host metadata and runtime database versions.
3. Create schemas and mandatory integrity indexes.

Deliverables: `docker-compose.yml`, `.env.example`, setup and security scripts.

## Phase 3 — canonical data and operations

1. Generate ID/seed-derived dimensions and order batches.
2. Load the identical logical facts sequentially into each database.
3. Run Q01–Q17 without and with workload indexes.

Deliverables: `benchmark/data_generator.py`, loaders, query catalogs and index files.

## Phase 4 — operational measurements

1. Sample host CPU/RAM and measure wall time with `perf_counter()`.
2. Collect data/index/total size.
3. Backup and restore to isolated databases; validate restored data.

Deliverables: raw/summary CSV, JSON metadata, backup/restore CSV.

## Phase 5 — analysis and academic handoff

1. Validate that every result is real and non-empty.
2. Generate final metric/query tables and charts from measured CSV only.
3. Inspect plans and resource evidence before causal interpretation.
4. Complete the conclusion and developer-effort diary score.

Deliverables: `report/measured_results.md`, `results/final_comparison.csv`, charts,
and the final updated conclusion. No result is entered before measurement.

