// Runs once, only on a fresh /data/db volume (see docker-entrypoint-initdb.d
// semantics of the official mongo image). Creates the application-level user
// that DataBackup/config.docker.yml expects, scoped to its own database
// (matches the app's authSource={db name} connection string).
const dbName = process.env.MONGO_APP_DB;
const appUser = process.env.MONGO_APP_USER;
const appPassword = process.env.MONGO_APP_PASSWORD;

db.getSiblingDB(dbName).createUser({
  user: appUser,
  pwd: appPassword,
  roles: [{ role: "readWrite", db: dbName }],
});
