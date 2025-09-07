from flask import Flask, request, jsonify
import psycopg2
import importlib.util
import os

app = Flask(__name__)

# TODO: Store in an env file. This is horribly unsafe.
DB_NAME = "database_version_2"
DB_USER = "postgres"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

# TODO: Find better solution for storing the list of games and their test.
games = {
    "conn4": {
        "module": "games.conn4.game",
        "tests": [ # Tuple data structure that decides the test items.
            ("minimax.py", "C4MinimaxAgent"),
            ("randomagent.py", "C4RandomAgent")
        ],
        "agent": "C4Agent"
    }
}

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    
def fetch_agents_by_group(groupname):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.agent_id, a.name, a.file_path
        FROM agents a
        JOIN groups g ON a.group_id = g.group_id
        WHERE g.groupname = %s;
    """, (groupname,))
    agents = cur.fetchall()
    cur.close()
    conn.close()
    return [{"agent_id": row[0], "name": row[1], "file_path": row[2]} for row in agents]

@app.route("/agents/<groupname>", methods=["GET"])
def get_agents(groupname):
    agents = fetch_agents_by_group(groupname)
    return jsonify(agents)

if __name__ == "__main__":
    app.run(debug=True)