# MongoDB backup and restore

```bash
docker compose exec -T mongodb mongodump \
  --username root --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin --db OnlineShopDB \
  --archive=/backups/OnlineShopDB_mongodb.archive.gz --gzip
```

Restore to an isolated database:

```bash
docker compose exec -T mongodb mongorestore \
  --username root --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --archive=/backups/OnlineShopDB_mongodb.archive.gz --gzip --drop \
  '--nsFrom=OnlineShopDB.*' '--nsTo=OnlineShopDB_restore.*'
```

For a write-active production replica set, use the documented oplog/consistent
backup procedure or a managed snapshot. Protect archives with filesystem/object
storage encryption and least-privilege access.

