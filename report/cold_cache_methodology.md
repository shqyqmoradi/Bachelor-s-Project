# Cold-cache methodology

Warm cache is the normal automated mode: each query receives one untimed warm-up,
then ten timed executions. It measures a stable, repeatedly accessed workload.

A portable and fair cold-cache test is not automated. `DBCC DROPCLEANBUFFERS` in
SQL Server, an operating-system page-cache drop for PostgreSQL, and process restart
for MongoDB do not evict equivalent layers and require different privileges. On
Docker Desktop, the Linux VM adds another cache layer. Calling these three actions
"the same" would be misleading.

If cold-cache evidence is required, use this protocol as a separate experiment:

1. Stop all three database containers.
2. Restart Docker Desktop/its VM to clear the shared guest page cache.
3. Start exactly one database, wait for health, run exactly one query once, stop it.
4. Restart the Docker VM before the next database/query.
5. Randomize database order, repeat at least five full rounds, and record restart
   duration separately from query duration.

Even then, storage-engine initialization and read-ahead differ. Results must be
labelled "cold-start approximation," not a perfectly controlled cold cache.

