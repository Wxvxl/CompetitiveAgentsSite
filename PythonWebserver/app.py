from flask import Flask, request, jsonify, session
from flask_cors import CORS
import importlib.util
import psycopg2
from psycopg2 import errors
import bcrypt
import os
from itertools import combinations
from collections import defaultdict


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://100.112.255.106:3000"], supports_credentials=True)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Use a strong secret in production

DB_URL = os.getenv("DATABASE_URL") # Setup the DB url in a .env

games = {
    "conn4": {
        "module": "games.conn4.game",
        "tests": [ # Tuple data structure that decides the test items.
            ("minimax.py", "C4MinimaxAgent"), # First entry is the test agent file, second is the class name.
            ("randomagent.py", "C4RandomAgent")
        ],
        "agent": "C4Agent" # The agent name for every student.
    },
    "tictactoe": {
       "module" : "games.tictactoe.game",
       "tests": [
           ("firstavail.py", "FirstAvailableAgent"),
           ("random.py", "RandomAgent") 
       ],
       "agent" : "TTTAgent"
    }
}

def get_db_connection():
    return psycopg2.connect(DB_URL)


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return None


def require_admin():
    auth_error = require_login()
    if auth_error:
        return auth_error
    if session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None
    
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

# newly added funtion to fetch the latest data:
def fetch_latest_agent(groupname, game):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""           
        SELECT a.agent_id, a.name, a.file_path
        FROM agents a
        JOIN groups g ON a.group_id = g.group_id
        WHERE g.groupname = %s
          AND a.game = %s 
        ORDER BY a.created_at DESC 
        LIMIT 1
    """, (groupname, game))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {"agent_id": row[0], "name": row[1], "file_path": row[2]}
    return None


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

    group_agent = fetch_latest_agent(groupname, game)
    if not group_agent:
        return {"error": f"No agent found for group: {groupname}"}

    group_file = group_agent["file_path"]
    group_class_name = game_info["agent"]

    results = {"group": groupname, "agent": group_agent["name"], "matches": []}

    GroupAgentClass = load_class_from_file(group_file, group_class_name)
    group_agent_name = group_agent["name"]

    for test_file, test_class in game_info["tests"]:
        test_path = os.path.join("games", game, "agents", "test", test_file)
        TestAgentClass = load_class_from_file(test_path, test_class)

        test_agent_name = test_class  # <- move inside the loop

        game_instance = GameClass(GroupAgentClass(), TestAgentClass())
        winner = game_instance.play()

        if winner == "X":
            winner_name = group_agent_name
        elif winner == "O":
            winner_name = test_agent_name
        else:
            winner_name = "Draw"
        
        results["matches"].append({
            "test_agent": test_agent_name,
            "winner": winner_name
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
    agent1 = fetch_latest_agent(group1, game)
    agent2 = fetch_latest_agent(group2, game)

    if not agent1:
        return {"error": f"No agent found for group: {group1}"}
    if not agent2:
        return {"error": f"No agent found for group: {group2}"}

    agent_class_name = game_info["agent"]

    # Load classes dynamically
    Agent1Class = load_class_from_file(agent1["file_path"], agent_class_name)
    Agent2Class = load_class_from_file(agent2["file_path"], agent_class_name)

    # Run the match
    game_instance = GameClass(Agent1Class(), Agent2Class())
    winner = game_instance.play()
    if winner == "X":
        winner_agent = agent1["name"]
    elif winner == "O":
        winner_agent = agent2["name"]
    else:
        winner_agent = "Draw"


    results = {
        "group1": {"name": group1, "agent": agent1["name"]},
        "group2": {"name": group2, "agent": agent2["name"]},
        "winner": winner_agent
    }

    return results

# agents win rate for leaderboard
def fetch_latest_agents_for_game(game: str):
    """Return the latest agent for every group for the specified game."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT ON (g.group_id)
                   a.agent_id,
                   a.name,
                   a.file_path,
                   g.groupname,
                   g.group_id
            FROM agents a
            JOIN groups g ON g.group_id = a.group_id
            WHERE a.game = %s
            ORDER BY g.group_id, a.created_at DESC, a.agent_id DESC;
            """,
            (game,),
        )
        rows = cur.fetchall()
        return [
            {
                "agent_id": row[0],
                "name": row[1],
                "file_path": row[2],
                "group": row[3],
                "group_id": row[4],
            }
            for row in rows
        ]
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def play_single_match(game_class, first_agent_cls, second_agent_cls):
    """Run a single match and return winner symbol: 'X', 'O', or 'Draw'."""
    game_instance = game_class(first_agent_cls(), second_agent_cls())
    return game_instance.play()


def run_round_robin_tournament(game: str):
    """
    Run a double tournament (each pair plays twice, swapping order)
    and return aggregated results
    """
    if game not in games:
        raise ValueError(f"Game '{game}' not found in configuration.")

    participants = fetch_latest_agents_for_game(game)
    if len(participants) < 2:
        raise ValueError("Need at least two agents to run a tournament.")

    game_info = games[game]
    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")
    agent_class_name = game_info["agent"]

    for participant in participants:
        participant["cls"] = load_class_from_file(participant["file_path"], agent_class_name)

    stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "games": 0})
    matches = []

    for agent_a, agent_b in combinations(participants, 2):
        ordered_pairs = [(agent_a, agent_b), (agent_b, agent_a)]
        for first, second in ordered_pairs:
            winner = play_single_match(GameClass, first["cls"], second["cls"])

            stats[first["group"]]["games"] += 1
            stats[second["group"]]["games"] += 1

            if winner == "X":
                stats[first["group"]]["wins"] += 1
                stats[second["group"]]["losses"] += 1
                winner_group = first["group"]
                winner_agent = first["name"]
            elif winner == "O":
                stats[second["group"]]["wins"] += 1
                stats[first["group"]]["losses"] += 1
                winner_group = second["group"]
                winner_agent = second["name"]
            else:
                stats[first["group"]]["draws"] += 1
                stats[second["group"]]["draws"] += 1
                winner_group = None
                winner_agent = None

            matches.append(
                {
                    "first_group": first["group"],
                    "first_agent": first["name"],
                    "second_group": second["group"],
                    "second_agent": second["name"],
                    "winner_symbol": winner,
                    "winner_group": winner_group,
                    "winner_agent": winner_agent,
                }
            )

    summary = []
    for group, data in stats.items():
        games_played = data["games"]
        win_rate = data["wins"] / games_played if games_played else 0.0
        summary.append(
            {
                "group": group,
                "wins": data["wins"],
                "losses": data["losses"],
                "draws": data["draws"],
                "games": games_played,
                "win_rate": win_rate,
            }
        )

    summary.sort(key=lambda item: (-item["win_rate"], -item["wins"], item["losses"]))

    return {
        "summary": summary,
        "matches": matches,
        "total_matches": len(matches),
    }


@app.route("/api/admin/tournaments/<game>/round_robin", methods=["POST"])
def run_round_robin_endpoint(game):
    auth_error = require_admin()
    if auth_error:
        return auth_error

    try:
        results = run_round_robin_tournament(game)
        return jsonify({"game": game, **results})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route("/api/admin/assign-group", methods=["POST"])
def assign_group():
    # Check admin authorization
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_id = data.get("user_id")
    group_id = data.get("group_id")

    if not user_id or group_id is None:
        return jsonify({"error": "Missing fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Update user's group
        cur.execute(
            "UPDATE users SET group_id = %s WHERE user_id = %s RETURNING user_id, username, email, role, group_id",
            (group_id, user_id)
        )
        
        updated_user = cur.fetchone()
        conn.commit()
        cur.close()

        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user": {
                "id": updated_user[0],
                "username": updated_user[1],
                "email": updated_user[2],
                "role": updated_user[3],
                "group_id": updated_user[4]
            }
        })

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/agents/upload/<game>", methods=["POST"])
def upload_agent(game):
    # Error Checking
    if "user_id" not in session:
        return {"error": "Not authenticated"}, 401
    if "group_id" not in session:
        return {"error": "Not in a group"}, 401
    if "file" not in request.files:
        return {"error": "No file part"}, 400

    file = request.files["file"]

    if file.filename == "":
        return {"error": "No selected file"}, 400
    if not file.filename.endswith(".py"):
        return {"error": "Only .py files allowed"}, 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT groupname FROM groups WHERE group_id = %s;", (session["group_id"],))
        group_name = cur.fetchone()[0]
        # File Upload
        path = os.path.join(os.getcwd(), "games", game, "agents", "students", group_name)
        os.makedirs(path, exist_ok=True)

        file.save(os.path.join(path, file.filename))
        
        cur.execute(
            """
            INSERT INTO agents (group_id, name, game, file_path)
            VALUES (%s, %s, %s, %s)
            RETURNING agent_id;
            """,
            (session["group_id"], file.filename[:-3], game, file.filename)
        )
                
        agent_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        
        return jsonify({
            "message": "File uploaded successfully",
            "agent": {
                "id": agent_id,
                "group_id" : session["group_id"],
                "file_path": file.filename,
                "game": game
            }
        })

    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500

    finally:
        if conn:
            conn.close()
    

@app.route("/agents/<groupname>/<game>", methods=["GET"])
def get_agents(groupname, game):
    try:
        agents = fetch_agents(groupname, game)
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

@app.route("/api/groups", methods=["GET"])
def list_groups():
    auth_error = require_login()
    if auth_error:
        return auth_error

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT group_id, groupname FROM groups ORDER BY groupname;")
        groups = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
        return jsonify({"groups": groups})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/create_group", methods=["POST"])
def create_group():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json or {}
    groupname = data.get("groupname")

    if not groupname:
        return jsonify({"error": "Group name required"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;",
            (groupname,)
        )
        group_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({
            "message": "Group created successfully",
            "group": {
                "id": group_id,
                "name": groupname,
            },
        })
    except errors.UniqueViolation:
        if conn:
            conn.rollback()
        return jsonify({"error": "Group name already exists"}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/users", methods=["GET"])
def list_users():
    auth_error = require_admin()
    if auth_error:
        return auth_error

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT u.user_id, u.username, u.email, u.role, u.group_id, g.groupname
            FROM users u
            LEFT JOIN groups g ON g.group_id = u.group_id
            WHERE u.role = 'student'
            ORDER BY u.username;
            """
        )
        users = [
            {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "group_id": row[4],
                "group_name": row[5],
            }
            for row in cur.fetchall()
        ]
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/users/<int:user_id>/group", methods=["PUT"])
def assign_user_group(user_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error

    data = request.json or {}
    group_id_raw = data.get("group_id")

    group_id = None
    if group_id_raw not in (None, "", "null"):
        try:
            group_id = int(group_id_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid group_id"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if group_id is not None:
            cur.execute("SELECT 1 FROM groups WHERE group_id = %s;", (group_id,))
            if cur.fetchone() is None:
                return jsonify({"error": "Group not found"}), 404

        cur.execute("SELECT role FROM users WHERE user_id = %s;", (user_id,))
        role_row = cur.fetchone()
        if role_row is None:
            return jsonify({"error": "User not found"}), 404
        if role_row[0] != "student":
            return jsonify({"error": "Only students can be assigned to a group"}), 400

        cur.execute(
            """
            UPDATE users
            SET group_id = %s
            WHERE user_id = %s
            RETURNING user_id, username, email, role, group_id;
            """,
            (group_id, user_id)
        )
        row = cur.fetchone()
        if row is None:
            conn.rollback()
            return jsonify({"error": "User not found"}), 404

        group_name = None
        if row[4] is not None:
            cur.execute("SELECT groupname FROM groups WHERE group_id = %s;", (row[4],))
            fetched = cur.fetchone()
            group_name = fetched[0] if fetched else None

        conn.commit()
        return jsonify(
            {
                "user": {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                    "group_id": row[4],
                    "group_name": group_name,
                }
            }
        )
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    
    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO users (username, email, hashed_password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id;
            """,
            (username, email, hashed_pw, role)
        )
        
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return jsonify({
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role,
            }
        }), 201
        
    except errors.UniqueViolation:
        if conn:
            conn.rollback()
        return jsonify({"error": "Username or Email already exists"}), 400

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn:
            conn.close()
        
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, email, role, group_id FROM users WHERE user_id = %s",
            (session["user_id"],)
        )
        user = cur.fetchone()
        cur.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user": {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[3],
                "group_id": user[4]
            }
        })
    finally:
        if conn:
            conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json 
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch user by email
        cur.execute(
            "SELECT user_id, username, email, hashed_password, role, group_id FROM users WHERE email = %s",
            (email,)
        )
        
        row = cur.fetchone()
        cur.close()

        if not row: 
            return jsonify({"error": "Invalid credentials"}), 401

        user_id, username, email_db, hashed_pw, role, group_id = row

        # Check password
        if not bcrypt.checkpw(password.encode(), hashed_pw.encode()):
            return jsonify({"error": "Invalid credentials"}), 401

        # Store info in session
        session["user_id"] = user_id
        session["email"] = email_db
        session["role"] = role
        session["group_id"] = group_id if group_id is not None else None

        return jsonify({
            "user": {
                "id": user_id,
                "username": username,
                "email": email_db,
                "role": role,
                "group_id": group_id if group_id is not None else None
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            
@app.route("/api/users", methods=["GET"])
def get_users():
    # Check admin authorization
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, email, role, group_id FROM users"
        )
        users = cur.fetchall()
        cur.close()

        return jsonify({
            "users": [
                {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "role": user[3],
                    "group_id": user[4]
                }
                for user in users
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/user/agents", methods=["GET"])
def get_user_agents():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if "group_id" not in session:
        return jsonify({"error": "Not in a group"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get group name for file path
        cur.execute("SELECT groupname FROM groups WHERE group_id = %s", (session["group_id"],))
        group_name = cur.fetchone()[0]
        
        # Get agents from database
        cur.execute("""
            SELECT agent_id, name, game, file_path, created_at 
            FROM agents 
            WHERE group_id = %s
            ORDER BY created_at DESC
        """, (session["group_id"],))
        
        agents = cur.fetchall()
        cur.close()

        return jsonify({
            "agents": [
                {
                    "id": agent[0],
                    "name": agent[1],
                    "game": agent[2],
                    "file_path": agent[3],
                    "created_at": agent[4].isoformat() if agent[4] else None
                }
                for agent in agents
            ]
        })
    except Exception as e:
        print(f"Error fetching agents: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            
@app.route("/api/admin/agents", methods=["GET"])
def get_all_agents():
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT a.agent_id, a.name, a.game, a.file_path, a.created_at, g.groupname
            FROM agents a
            JOIN groups g ON a.group_id = g.group_id
            ORDER BY a.created_at DESC
        """)
        
        agents = cur.fetchall()
        cur.close()

        return jsonify({
            "agents": [
                {
                    "id": agent[0],
                    "name": agent[1],
                    "game": agent[2],
                    "file_path": agent[3],
                    "created_at": agent[4].isoformat() if agent[4] else None,
                    "groupname": agent[5]
                }
                for agent in agents
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            
if __name__ == "__main__":
    app.run(debug=True)
