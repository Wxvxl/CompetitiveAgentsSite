import psycopg2

def insert_row(cursor, groupname, code):
    cursor.execute(f"""
        INSERT INTO scripts (groupname, code)
        VALUES (%s, %s)
    """, (groupname, code))


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

db_name = "testing_database"

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

cur.execute("""CREATE TABLE IF NOT EXISTS scripts (
                groupname VARCHAR(100) PRIMARY KEY,
                code TEXT
            );
        """)

insert_row(cur, "g1", """from PythonWebserver.baseclass import Agents
import random

class RandomAgents(Agents):
    choices = ["r", "p", "s"]
    def __init__(self):
        super().__init__()
    
    def getAction(self):
        return self.choices[random.randint(0,2)]
""")


insert_row(cur, "g2", """from PythonWebserver.baseclass import Agents
import random

class RandomAgents(Agents):
    choices = ["r", "p", "s"]
    def __init__(self):
        super().__init__()
    
    def getAction(self):
        return self.choices[random.randint(0,2)]
""")

conn.commit()
cur.close()
conn.close()

print("Success")