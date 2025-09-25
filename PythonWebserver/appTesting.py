#TODO: Rewrite the Testing Script to accomodate for new structure!
#TODO: Move Database Testing here!

#TODO: Rewrite the Testing Script to accomodate for new structure!
#TODO: Move Database Testing here!


import psycopg2
import os


user_name = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "admin")
host = "db"
port = "5432"
db_name = "test"

conn = psycopg2.connect(
    dbname=db_name,
    user=user_name,
    password=password,
    host=host,
    port=port
)
#conn.autocommit = True
cur = conn.cursor()

# Inserting Groups
cur.execute("INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;", ("group1",))
group1_id = cur.fetchone()[0]

cur.execute("INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;", ("group2",))
group2_id = cur.fetchone()[0]
conn.commit()


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


cur.close()
conn.close()
