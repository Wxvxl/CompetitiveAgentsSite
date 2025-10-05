import psycopg2
import os

DB_URL = os.getenv("DATABASE_URL")
user_name = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "admin")
host = "db"
port = "5432"
db_name = "test"

# Step 1: connect to default 'postgres' DB to create/drop 'test'
conn = psycopg2.connect(
    dbname="postgres",
    user=user_name,
    password=password,
    host=host,
    port=port
)

conn.autocommit = True
cur = conn.cursor()

# Drop + recreate database
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
if cur.fetchone():
    cur.execute(f"DROP DATABASE {db_name}")
cur.execute(f"CREATE DATABASE {db_name}")


# After creating database, close the first connection properly
cur.close()
conn.close()

# Step 2: connect directly to 'test' and build schema
conn = psycopg2.connect(
    dbname=db_name,
    user=user_name,
    password=password,
    host=host,
    port=port
)
cur = conn.cursor()

# Schema
# Drop existing tables first (in correct order due to foreign key constraints)
cur.execute("""
DROP TABLE IF EXISTS contest_actions CASCADE;
DROP TABLE IF EXISTS contests CASCADE;
DROP TABLE IF EXISTS agent_records CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS groups CASCADE;
""")

# Database setup code
# NOTE: Serial is better instead of integer, as serial is an automatic incrementer for user ID!
cur.execute("""
CREATE TABLE groups (
    group_id SERIAL PRIMARY KEY,
    groupname VARCHAR UNIQUE NOT NULL
);
""")

cur.execute("""
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    group_id INT REFERENCES groups(group_id) ON DELETE SET NULL
);
""")

cur.execute("""
CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    group_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    game varchar(50) NOT NULL,
    file_path varchar(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    agent1_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    agent2_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    group1_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    group2_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    played_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
""")

# Contest tables for FR3.x requirements
cur.execute("""
CREATE TABLE contests (
    contest_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game VARCHAR(50) NOT NULL,
    agent1_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    agent2_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    winner_id INT REFERENCES agents(agent_id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_by INT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE contest_actions (
    action_id SERIAL PRIMARY KEY,
    contest_id INT NOT NULL REFERENCES contests(contest_id) ON DELETE CASCADE,
    move_number INT NOT NULL,
    agent_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    action_data TEXT NOT NULL,
    board_state TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE agent_records (
    record_id SERIAL PRIMARY KEY,
    agent_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    UNIQUE(agent_id)
);
""")

conn.commit()
cur.close()
conn.close()

print("Database setup complete.")
