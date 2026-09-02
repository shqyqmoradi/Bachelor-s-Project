DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='shop_reader') THEN CREATE ROLE shop_reader NOLOGIN; END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='shop_writer') THEN CREATE ROLE shop_writer NOLOGIN; END IF;
END $$;
GRANT CONNECT ON DATABASE "OnlineShopDB" TO shop_reader, shop_writer;
GRANT USAGE ON SCHEMA public TO shop_reader, shop_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO shop_reader;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO shop_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO shop_reader;
-- LOGIN roles and SCRAM passwords should be provisioned from a secret manager.

