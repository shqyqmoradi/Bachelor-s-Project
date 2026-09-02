db = db.getSiblingDB("OnlineShopDB");
db.createRole({role:"shopReader",privileges:[{resource:{db:"OnlineShopDB",collection:""},actions:["find"]}],roles:[]});
db.createRole({role:"shopWriter",privileges:[{resource:{db:"OnlineShopDB",collection:""},actions:["find","insert","update","remove"]}],roles:[]});
// Create users interactively or through a secret manager; never commit production passwords.

