import psycopg2

conn = psycopg2.connect(
    dbname="testdb", user="postgres", password="admin", host="localhost"
)

cur = conn.cursor()

cur.execute("SELECT code FROM scripts WHERE name = %s", ("randomagent",))
result = cur.fetchone()

print(result[0])