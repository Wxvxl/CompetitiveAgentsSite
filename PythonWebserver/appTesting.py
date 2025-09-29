import os
import pytest
import bcrypt
import psycopg2
from flask import Flask
from app import app as flask_app, get_db_connection
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

# Clear database for testing.
cur.execute("DELETE FROM matches CASCADE;")
cur.execute("DELETE FROM agents CASCADE;")
cur.execute("DELETE FROM users CASCADE;")
cur.execute("DELETE FROM groups CASCADE;")
print("Database Cleared")

cur.execute("INSERT INTO groups (groupname) VALUES (%s) ON CONFLICT (groupname) DO NOTHING RETURNING group_id;", ("group1",))
group1_id = cur.fetchone()
if group1_id:
    group1_id = group1_id[0]
else:
    cur.execute("SELECT group_id FROM groups WHERE groupname = %s;", ("group1",))
    group1_id = cur.fetchone()[0]
print("Inserted Group 1")

cur.execute("INSERT INTO groups (groupname) VALUES (%s) ON CONFLICT (groupname) DO NOTHING RETURNING group_id;", ("group2",))
group2_id = cur.fetchone()
if group2_id:
    group2_id = group2_id[0]
else:
    cur.execute("SELECT group_id FROM groups WHERE groupname = %s;", ("group2",))
    group2_id = cur.fetchone()[0]
print("Inserted Group 2")

cur.execute("SELECT * FROM groups;")
groups_in_db = cur.fetchall()

assert len(groups_in_db) >= 2, "At least 2 groups should be inserted"
group_names = [g[1] for g in groups_in_db]
assert "group1" in group_names, "group1 should be in groups"
assert "group2" in group_names, "group2 should be in groups"


users = [
    ("user1", "user1@example.com", "password1", "student", group1_id),
    ("user2", "user2@example.com", "password2", "student", group1_id),
    ("user3", "user3@example.com", "password3", "student", group2_id),
    ("user4", "user4@example.com", "password4", "student", group2_id),
]

for username, email, password, role, group_id in users:
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute(
        """
        INSERT INTO users (username, email, hashed_password, role, group_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
        """,
        (username, email, hashed_pw, role, group_id)
    )

print("Inserted Users")

cur.execute("SELECT * FROM users;")
users_in_db = cur.fetchall()
assert len(users_in_db) >= 4, "At least 4 users should be inserted"
usernames = [u[1] for u in users_in_db]
assert "user1" in usernames, "user1 should be in users"
assert "user2" in usernames, "user2 should be in users"
assert "user3" in usernames, "user3 should be in users"
assert "user4" in usernames, "user4 should be in users"


base_path = os.path.join(os.getcwd(), "games")

cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group1_id, "group1agent", "conn4", os.path.join(base_path, "conn4", "agents", "students", "group1", "group1agent.py"))
)

cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group1_id, "g1agent", "TTT", os.path.join(base_path, "tictactoe", "agents", "students", "group1", "g1agent.py"))
)


cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group2_id, "group2agent", "conn4", os.path.join(base_path, "conn4", "agents", "students", "group2", "group2agent.py"))
)

cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group2_id, "g2agent", "TTT", os.path.join(base_path, "tictactoe", "agents", "students", "group2", "g2agent.py"))
)

print("Inserted Agents")

cur.execute("SELECT * FROM agents;")
agents_in_db = cur.fetchall()
assert len(agents_in_db) >= 4, "At least 4 agents should be inserted"
agent_names = [a[2] for a in agents_in_db]
assert "group1agent" in agent_names, "group1agent should be in agents"
assert "g1agent" in agent_names, "g1agent should be in agents"
assert "group2agent" in agent_names, "group2agent should be in agents"
assert "g2agent" in agent_names, "g2agent should be in agents"

print("All pytest checks passed!")

cur.close()
conn.close()