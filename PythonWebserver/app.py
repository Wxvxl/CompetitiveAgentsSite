from flask import Flask, request, jsonify, session
from flask_cors import CORS
from models import SessionLocal, User, Agent
from sqlalchemy.exc import IntegrityError
import importlib.util
import psycopg2
import bcrypt
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"],supports_credentials=True)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Use a strong secret in production


UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploaded_agents")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/api/upload_agent", methods=["POST"])
def upload_agent():
    if "user_id" not in session:
        return {"error": "Not authenticated"}, 401
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400
    if not file.filename.endswith(".py"):
        return {"error": "Only .py files allowed"}, 400
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)
    db = SessionLocal()
    agent = Agent(filename=file.filename, user_id=session["user_id"])
    db.add(agent)
    db.commit()
    db.close()
    return {"message": "Agent uploaded successfully", "filename": file.filename}

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role = data.get("role", "student")
    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db = SessionLocal()
    user = User(email=email, password=hashed_pw, name=name, role=role)
    db.add(user)
    try:
        db.commit()
        return jsonify({"user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}})
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Email already exists"}), 400
    finally:
        db.close()
        
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "user": {
            "id": session["user_id"],
            "email": session["email"],
            "isAdmin": session["isAdmin"]
        }
    })

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({"error": "Invalid credentials"}), 401
    session["user_id"] = user.id
    session["email"] = user.email
    session["isAdmin"] = user.isAdmin
    session["role"] = user.role  
    return jsonify({
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "isAdmin": user.isAdmin,
            "role": user.role     
        }
    })


@app.route("/api/agents", methods=["GET"])
def list_agents():
    db = SessionLocal()
    agents = db.query(Agent).join(User).all()
    result = [
        {
            "id": agent.id,
            "filename": agent.filename,
            "uploader": agent.user.email,
            "upload_time": agent.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for agent in agents
    ]
    db.close()
    return jsonify(result)

# TODO: Store in an env file. This is horribly unsafe.
DB_NAME = "database_version_2"
DB_USER = "postgres"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

# TODO: Find better solution for storing the list of games and their test.
# Maybe a JSON file or just store it in the DB.
games = {
    "conn4": {
        "module": "games.conn4.game",
        "tests": [ # Tuple data structure that decides the test items.
            ("minimax.py", "C4MinimaxAgent"), # First entry is the test agent file, second is the class name.
            ("randomagent.py", "C4RandomAgent")
        ],
        "agent": "C4Agent" # The agent name for every student.
    },
    "TTT": {
       "module" : "games.tictactoe.game",
       "tests": [
           ("firstavail.py", "FirstAvailableAgent"),
           ("random.py", "RandomAgent") 
       ],
       "agent" : "TTTAgent"
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
    
# Fetch an agent from a group for a specific game
def fetch_agents(groupname, game):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.agent_id, a.name, a.file_path
        FROM agents a
        JOIN groups g ON a.group_id = g.group_id
        WHERE g.groupname = %s
          AND a.game = %s ;
    """, (groupname, game))
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

def run_tests_on_group(groupname, game):
    if game not in games:
        raise ValueError(f"Game '{game}' not found in configuration.")
    game_info = games[game]

    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")

    agents = fetch_agents(groupname, game)
    if not agents:
        return {"error": f"No agents found for group: {groupname}"}

    group_agent = agents[0]  #TODO: Write code to pick the latest agent from the DB.
    group_file = group_agent["file_path"]
    group_class_name = game_info["agent"]

    results = {"group": groupname, "agent": group_agent["name"], "matches": []}

    GroupAgentClass = load_class_from_file(group_file, group_class_name)

    for test_file, test_class in game_info["tests"]:
        test_path = os.path.join("games", game, "agents", "test", test_file)
        TestAgentClass = load_class_from_file(test_path, test_class)

        game_instance = GameClass(GroupAgentClass(), TestAgentClass())
        winner = game_instance.play()

        results["matches"].append({
            "test_agent": test_class,
            "winner": winner
        })

    return results

def run_group_vs_group(group1, group2, game):
    if game not in games:
        raise ValueError(f"Game '{game}' not found in configuration.")
    game_info = games[game]

    # Load Game class
    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")

    # Fetch agents from each group
    agents1 = fetch_agents(group1, game)
    agents2 = fetch_agents(group2, game)

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