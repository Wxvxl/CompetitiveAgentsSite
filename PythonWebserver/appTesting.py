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

base_path = os.path.join(os.getcwd(), "games")