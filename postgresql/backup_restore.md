# PostgreSQL backup and restore

Custom format permits validation and flexible restore:

```bash
docker compose exec -T postgres pg_dump -U postgres -Fc \
  -f /backups/OnlineShopDB_postgresql.dump OnlineShopDB
docker compose exec -T postgres pg_restore -l /backups/OnlineShopDB_postgresql.dump >/dev/null
```

Restore into a separate database:

```bash
docker compose exec -T postgres dropdb -U postgres --if-exists OnlineShopDB_restore
docker compose exec -T postgres createdb -U postgres OnlineShopDB_restore
docker compose exec -T postgres pg_restore -U postgres -d OnlineShopDB_restore \
  /backups/OnlineShopDB_postgresql.dump
```

`pg_dump` is a logical backup and does not replace WAL archiving/PITR. Encrypt the
backup file with an external key-management process for production.

