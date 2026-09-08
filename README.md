# B.Sc. Computer Engineering (IT) final project-Shiraz University 

## Practical Comparison of SQL Server, PostgreSQL and MongoDB

**Author:** Shaghayegh Alimoradi  
**Supervisor:** Dr. Taghizadeh

This is a B.Sc. Computer Engineering (IT) final project at Shiraz University.

This project compares three database management systems, `SQL Server`, `PostgreSQL`, and `MongoDB`, using the same online shop scenario.

The primary goal is to evaluate the differences between these systems in terms of data modeling, query performance, index impact, insert/update/delete execution time, resource consumption, storage size, and backup/restore performance.

## Online Shop Structure

The project model includes 8 core entities:

- Customers
- Categories
- Products
- Orders
- OrderItems
- Payments
- Addresses
- Shipment

`SQL Server` and `PostgreSQL` use the relational model.

`MongoDB` uses a document model with embedded documents and references.

## Benchmark Design

The main project results were collected using 100,000 orders.

The following fixed seed is used to generate identical data for all three systems:

```text
20260830
```

Each order contains between 1 and 5 items.

A total of 16 benchmark operations are included:

- 13 read and aggregation operations
- Insert
- Update
- Delete

Each read operation is executed 10 times after a warm-up run.

The benchmark is executed in two stages:

1. With only the required primary indexes
2. With additional workload-specific indexes

## Versions Used

| Database | Version |
|---|---|
| SQL Server | SQL Server 2022 |
| PostgreSQL | PostgreSQL 16.4 |
| MongoDB | MongoDB 7.0.14 |

The databases run using Docker.

## Prerequisites

- Docker Desktop
- Python 3.11 or 3.12
- Microsoft ODBC Driver 18 for SQL Server
- GNU Make

Install the driver on macOS:

```bash
brew install unixodbc
brew install --cask microsoft-odbc-driver-for-sql-server
```

## Running the Project

First, create the environment file:

```bash
make env
```

Then start the services:

```bash
make up
```

Check the container status:

```bash
docker compose ps
```

Run the main benchmark:

```bash
ORDERS=100000 REPETITIONS=10 make benchmark
```

Run it directly with Python:

```bash
.venv/bin/python -m benchmark.run_all --orders 100000
```

## Backup and Restore

Run the backup and restore test:

```bash
.venv/bin/python -m benchmark.backup_restore_benchmark
```

Results are stored in:

```text
results/
```

## Main Outputs

The main result files are:

```text
results/raw_results.csv
results/summary_results.csv
results/insert_results.csv
results/storage_results.csv
results/environment.json
results/backup_restore_results.csv
results/restore_validation.csv
results/final_comparison.csv
```

Validate the results:

```bash
make validate
```

Run the final analysis:

```bash
make analyze
```

## Project Structure

```text
benchmark/       benchmark scripts and data generator
mongodb/         MongoDB schema, queries and indexes
postgresql/      PostgreSQL schema, queries and indexes
results/         benchmark results
sqlserver/       SQL Server schema, queries and indexes
.env.example     environment configuration example
.gitignore
docker-compose.yml
Makefile
README.md
requirements.txt
```

## Runtime Environment Note

On Macs with Apple Silicon, SQL Server runs through emulation because its official image is based on the `amd64` architecture.

Therefore, performance results on Apple Silicon may not be fully representative. For more accurate benchmarking, an `x86-64` system is recommended.

## Cleanup

Stop the services:

```bash
make down
```

Remove the test volumes:

```bash
docker compose down -v
```

This project provides a practical comparison of three database systems in a consistent environment and examines the differences between relational and document models.
