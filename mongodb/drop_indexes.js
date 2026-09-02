db = db.getSiblingDB("OnlineShopDB");
for (const c of ["customers", "products", "orders"]) {
  for (const index of db[c].getIndexes()) {
    if (!index.name.startsWith("_id_") && !index.name.startsWith("ux_")) db[c].dropIndex(index.name);
  }
}
