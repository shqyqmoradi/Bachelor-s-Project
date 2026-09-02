# SQL Server backup and restore

The compose bind mount maps `./backups` to `/var/opt/mssql/backup`. The commands
below use checksums and compression. Test credentials are read from `.env`.

```bash
docker compose exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C \
  -Q "BACKUP DATABASE OnlineShopDB TO DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH INIT, COMPRESSION, CHECKSUM"
```

Verify before restore:

```bash
docker compose exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C \
  -Q "RESTORE VERIFYONLY FROM DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak' WITH CHECKSUM"
```

Restore to an isolated name so the source remains available:

```sql
RESTORE DATABASE OnlineShopDB_restore
FROM DISK='/var/opt/mssql/backup/OnlineShopDB_sqlserver.bak'
WITH MOVE 'OnlineShopDB' TO '/var/opt/mssql/data/OnlineShopDB_restore.mdf',
     MOVE 'OnlineShopDB_log' TO '/var/opt/mssql/data/OnlineShopDB_restore_log.ldf',
     RECOVERY;
```

For production, encrypt backups and protect both the certificate/key and media;
test restores regularly. The Developer edition in this lab is not licensed for production.

