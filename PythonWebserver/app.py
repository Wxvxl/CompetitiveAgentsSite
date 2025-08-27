from flask import Flask, request, jsonify
from game import RockPaperScissorGame
import psycopg2

app = Flask(__name__)

db_name = "testing_database"
def get_db_connection():
    conn = psycopg2.connect(
        dbname=db_name,       
        user="postgres",     
        password="admin", 
        host="localhost"     
    )
    return conn

def load_agent(name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT code FROM scripts WHERE name = %s", (name,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise ValueError(f"No script found with name '{name}'")

    code = row[0]
    namespace = {}
    exec(code, namespace) 

    agent_class = None
    for obj in namespace.values():
        if isinstance(obj, type) and obj.__name__ != "Agents":
            agent_class = obj
            break


    if agent_class is None:
        raise ValueError("No class found in retrieved script")

    agent_instance = agent_class()
    return agent_instance

@app.route("/upload", methods=["POST"])
def upload_script():
    data = request.json
    name = data.get("name")
    code = data.get("code")
    groupname = data.get("groupname", "defaultgroup")

    if not name or not code:
        return jsonify({"error": "name and code are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO scripts (name, code, groupname)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET code = EXCLUDED.code,
                groupname = EXCLUDED.groupname
            """,
            (name, code, groupname)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({"status": "ok", "message": f"Script '{name}' stored successfully."})

@app.route("/scripts", methods=["GET"])
def list_scripts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, groupname, code FROM scripts")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    scripts = [
        {
            "id": r[0],
            "name": r[1],
            "groupname": r[2],
            "code": r[3],
        }
        for r in rows
    ]
    return jsonify(scripts)

@app.route("/compete/<agent1>/<agent2>", methods=["GET"])
def compete(agent1, agent2):
    game = RockPaperScissorGame()
    agent1_class = load_agent(agent1)
    agent2_class = load_agent(agent2)
    
    game.assignPlayers(agent1_class, agent2_class)
    return game.startGame(5)
    
if __name__ == "__main__":
    app.run(debug=True)