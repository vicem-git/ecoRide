db = db.getSiblingDB(process.env.MONGO_DB);

db.createUser({
  user: process.env.MONGO_USER,
  pwd: process.env.MONGO_PASS,
  roles: [{ role: "readWrite", db: process.env.MONGO_DB }]
});

print("FLASK USER CREATED SUCCESSFULLY")

