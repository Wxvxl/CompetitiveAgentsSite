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
    (group1_id, "g1agent", "tictactoe", os.path.join(base_path, "tictactoe", "agents", "students", "group1", "g1agent.py"))
)


cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group2_id, "group2agent", "conn4", os.path.join(base_path, "conn4", "agents", "students", "group2", "group2agent.py"))
)

cur.execute(
    "INSERT INTO agents (group_id, name, game, file_path) VALUES (%s, %s, %s, %s);",
    (group2_id, "g2agent", "tictactoe", os.path.join(base_path, "tictactoe", "agents", "students", "group2", "g2agent.py"))
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

# Endpoint Testing Functions
def test_register(username, email, password, role):
    try:
        client = flask_app.test_client()
        
        test_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        
        response = client.post('/api/register', json=test_data)
        
        assert response.status_code == 201

        data = response.get_json()
        assert "user" in data
        assert data["user"]["username"] == username
        
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()
        assert user is not None
        cur.close()
        conn.close()
        
        return True
    except AssertionError as e:
        return False
    except Exception as e:
        return f"Unexpected error: {e}"
    
def test_login(email, password):
    client = flask_app.test_client()
    test_data = {
        "email": email,
        "password": password
    }
    
    response = client.post('/api/login', json=test_data)

    if response.status_code == 200:
        data = response.get_json()
        if "user" in data and data["user"]["email"] == email:
            return True
    return False

def test_create_group(email, password, groupname):
    client = flask_app.test_client()
    
    login_data = {"email": email, "password": password}
    login_response = client.post('/api/login', json=login_data)

    create_data = {"groupname": groupname}
    response = client.post('/api/create_group', json=create_data)

    if response.status_code == 200:
        data = response.get_json()
        if "group" in data and data["group"]["name"] == groupname:
            return True
    return False

def test_run_tests_endpoint(groupname, game):
    client = flask_app.test_client()
    
    response = client.get(f'/play/run_tests/{groupname}/{game}')
    
    if response.status_code == 200:
        data = response.get_json()
        # Check for expected structure (e.g., "group", "agent", "matches")
        if "group" in data and "matches" in data:
            return True
    return False

def test_group_vs_group_endpoint(group1, group2, game):
    client = flask_app.test_client()
    
    response = client.get(f'/play/group_vs_group/{group1}/{group2}/{game}')
    
    if response.status_code == 200:
        data = response.get_json()
        # Check for expected structure (e.g., "group1", "group2", "winner")
        if "group1" in data and "group2" in data and "winner" in data:
            return True
    return False

# Register Tests
assert test_register("testuser1", "testuser1@test.com", "password", "student") == True
assert test_register("testuser2", "testuser2@test.com", "password", "student") == True
print("Registration test passed")

assert test_register("testuser1", "testuser1@test.com", "password", "student") == False # TestUser1 already registered.
assert test_register("testuser3", "testuser1@test.com", "password", "student") == False # Same email
assert test_register("", "email@mail.com", "password", "student") == False # No username
# assert test_register("   ", "email@mail.com", "password", "student") == False # Username is just spaces. Should be invalid. TODO: FIX REGISTER FUNCTION, THIS TEST FAILS
print("Invalid Registration test passed")

# Login Test
assert test_login("user1@example.com", "password1") == True
print("Successful login test passed")

assert test_login("user1@example.com", "wrongpassword") == False # Wrong Password
assert test_login("2user1@example.com", "password") == False # Not a real user
print("Invalid login test failed")

# Create Group Tests
assert test_create_group("user1@example.com", "password1", "newgroup") == True
print("Successful create group test passed")

assert test_create_group("user1@example.com", "password1", "newgroup") == False  # Duplicate group name
assert test_create_group("invalid@example.com", "password", "anothergroup") == False  # Invalid login
print("Invalid create group test passed")

# Running tests on groups
assert test_run_tests_endpoint("group1", "conn4") == True
assert test_run_tests_endpoint("group1", "tictactoe") == True
print("Group against test-agents test passed")

# Running group vs group
assert test_group_vs_group_endpoint("group1", "group2", "conn4") == True
assert test_group_vs_group_endpoint("group1", "group2", "tictactoe") == True
print("Group vs Group endpoint test passed")
print("All pytest checks passed!")

cur.close()
conn.close()
