USE OnlineShopDB;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name='shop_reader') CREATE ROLE shop_reader;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name='shop_writer') CREATE ROLE shop_writer;
GRANT SELECT ON SCHEMA::dbo TO shop_reader;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO shop_writer;
-- Create logins/users separately with secrets from a secure vault; do not embed production passwords here.

