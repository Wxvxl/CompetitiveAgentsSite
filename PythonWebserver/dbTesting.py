import psycopg2

# Replace this with your postgres password during setup.
user_name = "postgres"
password = "admin"

conn = psycopg2.connect(
    dbname="postgres",
    user=user_name,
    password=password,
    host="localhost",
    port="5432"
)

conn.autocommit = True
cur = conn.cursor()

db_name = "database_version_2"
    
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")

if cur.fetchone():
    cur.execute(f"DROP DATABASE {db_name}")
    
cur.execute(f"CREATE DATABASE {db_name}")

conn = psycopg2.connect(
    dbname=db_name,
    user=user_name,
    password=password, 
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Database setup code
# NOTE: Serial is better instead of integer, as serial is an automatic incrementer for user ID!
cur.execute("""
CREATE TABLE groups (
    group_id SERIAL PRIMARY KEY,
    groupname VARCHAR UNIQUE NOT NULL
);
""")

# NOTE: All of the table should be VARCHAR! String is unlimited length!
# Role and IsAdmin can be merged.
# Agents shouldn't be related to users instead be connected to groups only.
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
    filename varchar(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    agent1_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    agent2_id INT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    group1_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    group2_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Database Testing Insert Scripts

# Inserting Groups
cur.execute("INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;", ("group1",))
group1_id = cur.fetchone()[0]

cur.execute("INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;", ("group2",))
group2_id = cur.fetchone()[0]

# TODO: Agent insertion is currently unavailable!
# # Inserting Agents
# cur.execute("""
#     INSERT INTO agents (group_id, name, game, file_path)
#     VALUES (%s, %s, %s, %s)
#     RETURNING agent_id;
# """, (group1_id, "Group 1 Agent", "conn4","games/conn4/agents/students/group1/group1agent.py"))

# cur.execute("""
#     INSERT INTO agents (group_id, name, game, file_path)
#     VALUES (%s, %s, %s, %s)
#     RETURNING agent_id;
# """, (group2_id, "Group 2 Agent", "conn4","games/conn4/agents/students/group2/group2agent.py"))

# conn.commit()

# Testing Code
# Fetch groups
print("=== Groups ===")
cur.execute("SELECT * FROM groups;")
for row in cur.fetchall():
    print(f"group_id={row[0]}, groupname={row[1]}")

# # Fetch agents
# print("\n=== Agents ===")
# cur.execute("""
#     SELECT a.agent_id, a.name AS agent_name, a.file_path, g.groupname, a.game
#     FROM agents a
#     JOIN groups g ON a.group_id = g.group_id;
# """)
# for row in cur.fetchall():
#     print(f"agent_id={row[0]}, agent_name={row[1]}, file_path={row[2]}, groupname={row[3]}, game={row[4]}")

print("Success")