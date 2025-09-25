# 📦 Database Container Setup

This project uses **PostgreSQL in Docker** with a Python script to automatically set up the database and schema.

---

## 🚀 Getting Started

### 1. Environment Variables

Set your database credentials in a `.env` file (example used for testing):

```env
POSTGRES_DB=test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
SECRET_KEY=super-secret-key
DATABASE_URL=postgresql://postgres:admin@db:5432/test
```

These values are read by the Python script and the Postgres container.

---

### 2. Build & Run Containers
Start everything with:

```bash
docker compose up --build
```

---

### 3. Database Initialization

Run it inside the container:

```bash
docker compose exec app python dbTesting.py
```

You should see:

```
✅ Database setup complete.
```

---

### 4. Verify the Database

You can connect to the DB with `psql`:

```bash
docker compose exec db psql -U $POSTGRES_USER -d test
```

Check tables:

```sql
\dt;
```

---

## 🗂 Schema Overview

* **groups** → stores group info.
* **users** → user accounts linked optionally to groups.
* **agents** → game agents belonging to groups.
* **matches** → match records between agents.

---

## 🛠 Development Notes

* Don’t use the default `postgres` database for application data — it’s reserved for admin tasks.
* The `test` DB is recreated each time `dbTesting.py` runs (good for CI/testing).
---

## 🌀 If You Change Only the Python Script 
Re-run it inside the container:
```
docker compose exec app python <file>
```
This will drop/recreate the test database and rebuild the schema.

## 🌀 If You Change the Dockerfile or Dependencies
Rebuild the image:
```
docker compose build app
docker compose up -d
```
