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

def load_class_from_file(filepath, class_name):
    """Dynamically load a class from a file."""
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

def run_tests_on_group(groupname, game_key):
    if game_key not in games:
        raise ValueError(f"Game '{game_key}' not found in configuration.")
    game_info = games[game_key]

    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")

    agents = fetch_agents_by_group(groupname)
    if not agents:
        return {"error": f"No agents found for group: {groupname}"}

    group_agent = agents[0]  #TODO: Write code to pick the latest agent from the DB.
    group_file = group_agent["file_path"]
    group_class_name = game_info["agent"]

    results = {"group": groupname, "agent": group_agent["name"], "matches": []}

    GroupAgentClass = load_class_from_file(group_file, group_class_name)

    for test_file, test_class in game_info["tests"]:
        test_path = os.path.join("games", game_key, "agents", "test", test_file)
        TestAgentClass = load_class_from_file(test_path, test_class)

        game_instance = GameClass(GroupAgentClass(), TestAgentClass())
        winner = game_instance.play()

        results["matches"].append({
            "test_agent": test_class,
            "winner": winner
        })

    return results

def run_group_vs_group(group1, group2, game_key):
    if game_key not in games:
        raise ValueError(f"Game '{game_key}' not found in configuration.")
    game_info = games[game_key]

    # Load Game class
    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")

    # Fetch agents from each group
    agents1 = fetch_agents_by_group(group1)
    agents2 = fetch_agents_by_group(group2)

    if not agents1:
        return {"error": f"No agents found for group: {group1}"}
    if not agents2:
        return {"error": f"No agents found for group: {group2}"}

    # TODO: refine later, just pick index 0 for now
    agent1 = agents1[0]
    agent2 = agents2[0]

    agent_class_name = game_info["agent"]

    # Load classes dynamically
    Agent1Class = load_class_from_file(agent1["file_path"], agent_class_name)
    Agent2Class = load_class_from_file(agent2["file_path"], agent_class_name)

    # Run the match
    game_instance = GameClass(Agent1Class(), Agent2Class())
    winner = game_instance.play()

    results = {
        "group1": {"name": group1, "agent": agent1["name"]},
        "group2": {"name": group2, "agent": agent2["name"]},
        "winner": winner
    }

    return results

@app.route("/agents/<groupname>", methods=["GET"])
def get_agents(groupname):
    try:
        agents = fetch_agents_by_group(groupname)
        return jsonify(agents)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route("/play/run_tests/<groupname>/<game>", methods=["GET"])
def play_group_vs_tests(groupname, game):
    try:
        results = run_tests_on_group(groupname, game)
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    
@app.route("/play/group_vs_group/<group1>/<group2>/<game>", methods=["GET"])
def play_group_vs_group(group1, group2, game):
    try:
        results = run_group_vs_group(group1, group2, game)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)