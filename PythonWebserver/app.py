from flask import Flask, request, jsonify, session
from flask_cors import CORS
import importlib.util
import psycopg2
from psycopg2 import errors
from psycopg2.extras import execute_batch
import bcrypt
import os
import random
import math
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://100.112.255.106:3000"], supports_credentials=True)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Use a strong secret in production

DB_URL = os.getenv("DATABASE_URL") # Setup the DB url in a .env

games = {
    "conn4": {
        "module": "games.conn4.game",
        "tests": [ # Tuple data structure that decides the test items.
            ("minimax.py", "C4MinimaxAgent"), # First entry is the test agent file, second is the class name.
            ("randomagent.py", "C4RandomAgent")
        ],
        "gamesize" : 2, # Number of players
        "agent": "C4Agent" # The agent name for every student.
    },
    "tictactoe": {
       "module" : "games.tictactoe.game",
       "tests": [
           ("firstavail.py", "FirstAvailableAgent"),
           ("random.py", "RandomAgent") 
       ],
       "gamesize" : 2, # Number of players
       "agent" : "TTTAgent"
    }
}

def get_db_connection():
    return psycopg2.connect(DB_URL)
    
def fetch_agents(groupname, game):
    """
    Fetch the list of all agents in the database for a specific group and game.
    
    Args :
        groupname (str)
        game (str) : ID of the game, this must be one of the valid games in the games dict defined above

    Raises :
        # TODO: Write error checking code for this function
        
    Returns:
        List : List that each contain a dictionary that has three keys: agent_id, name, and file_path for each agent.
    """
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

def fetch_latest_agent(groupname, game):
    """
    Fetch only the latest agents from the specified group for a specific game.
    
    Args:
        groupname (str)
        game (str) : ID of the game, this must be one of the valid games in the games dict defined above
        
    Raises:
        #TODO: Write error checking code for this function.
    
    Returns:
       Dict : Return a single dictionary that contains the agent_id, name, and file_path information 
    """
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

# ------ Tournament Functions Below ------ #    

def fetch_latest_agents_for_game(cur, game):
    """Return each group's most recently uploaded agent metadata for the given game."""
    cur.execute(
        """
        SELECT DISTINCT ON (g.group_id)
            a.agent_id,
            a.group_id,
            g.groupname,
            a.name,
            a.file_path
        FROM agents a
        JOIN groups g ON a.group_id = g.group_id
        WHERE a.game = %s
        ORDER BY g.group_id, a.created_at DESC;
        """,
        (game,)
    )
    rows = cur.fetchall()
    return [
        {
            "agent_id": row[0],
            "group_id": row[1],
            "groupname": row[2],
            "agent_name": row[3],
            "file_path": row[4],
        }
        for row in rows
    ]


def resolve_agent_path(game, groupname, file_path):
    """Resolve agent file path relative to game/student folders when a raw path is provided."""
    if not file_path:
        return file_path

    if os.path.isabs(file_path):
        return file_path if os.path.exists(file_path) else file_path

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    search_candidates = [
        os.path.join(current_dir, "games", game, "agents", "students", groupname, file_path),
        os.path.join(project_root, "games", game, "agents", "students", groupname, file_path),
        os.path.join(current_dir, file_path),
        os.path.join(project_root, file_path),
    ]

    for candidate in search_candidates:
        if os.path.exists(candidate):
            return os.path.abspath(candidate)

    return file_path


def load_agent_class(filepath, class_name):
    """Import the agent class from a concrete file path, raising if the file is missing."""
    if not filepath:
        raise FileNotFoundError("Agent file path is missing.")

    full_path = os.path.abspath(filepath)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Agent file not found: {full_path}")

    return load_class_from_file(full_path, class_name)


def play_agents_match(agent1_info, agent2_info, game):
    """Execute a single game between two latest agents and return normalized scoring metadata.

    Note:
        Reusing the higher-level endpoint helper would require extra lookups/mocking that
        reintroduce complexity and duplicated state.
    """
    if game not in games:
        raise ValueError(f"Game '{game}' not found in configuration.")

    game_info = games[game]
    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")
    agent_class_name = game_info["agent"]

    agent1_path = resolve_agent_path(game, agent1_info["groupname"], agent1_info["file_path"])
    agent2_path = resolve_agent_path(game, agent2_info["groupname"], agent2_info["file_path"])

    Agent1Class = load_agent_class(agent1_path, agent_class_name)
    Agent2Class = load_agent_class(agent2_path, agent_class_name)

    game_instance = GameClass([Agent1Class(), Agent2Class()])

    result_payload = game_instance.play()

    winner_agent_id = None
    agent1_score = 0
    agent2_score = 0
    result_key = "draw"
    winner_label = "Draw"

    if isinstance(result_payload, (list, tuple)) and result_payload:
        winner_index = result_payload[0]
        if winner_index in (0, 1):
            if winner_index == 0:
                winner_agent_id = agent1_info["agent_id"]
                agent1_score, agent2_score = 1, 0
                result_key = "agent1"
                winner_label = agent1_info["agent_name"]
            else:
                winner_agent_id = agent2_info["agent_id"]
                agent1_score, agent2_score = 0, 1
                result_key = "agent2"
                winner_label = agent2_info["agent_name"]
    else:
        # Unsupported result types are treated as draw for safety.
        result_payload = None

    return {
        "winner_agent_id": winner_agent_id,
        "agent1_score": agent1_score,
        "agent2_score": agent2_score,
        "result": result_key,
        "winner_label": winner_label,
        "raw_winner": result_payload, # Preserve engine-native outcome for debugging/audit trails.
    }


def initialize_tournament_standings(cur, tournament_id, agents):
    """Seed standing rows (DB + in-memory) with zero points for all participating agents."""
    if not agents:
        return {}

    execute_batch(
        cur,
        """
        INSERT INTO tournament_standings (tournament_id, agent_id, points, rounds_played)
        VALUES (%s, %s, 0, 0)
        ON CONFLICT (tournament_id, agent_id)
        DO UPDATE SET points = EXCLUDED.points, rounds_played = EXCLUDED.rounds_played;
        """,
        [(tournament_id, agent["agent_id"]) for agent in agents],
    )

    return {
        agent["agent_id"]: {
            "agent_id": agent["agent_id"],
            "group_id": agent["group_id"],
            "groupname": agent["groupname"],
            "agent_name": agent["agent_name"],
            "file_path": agent["file_path"],
            "points": 0,
            "rounds_played": 0,
        }
        for agent in agents
    }


def update_standing(cur, standings, tournament_id, agent_id, points_increment, opponent_id=None):
    """Apply a point delta for an agent, tracking rounds-played and opponent history."""
    entry = standings[agent_id]
    increment = int(points_increment)
    entry["points"] += increment
    entry["rounds_played"] += 1
    cur.execute(
        """
        UPDATE tournament_standings
        SET points = points + %s,
            rounds_played = rounds_played + 1,
            last_updated = CURRENT_TIMESTAMP
        WHERE tournament_id = %s AND agent_id = %s
        """,
        (increment, tournament_id, agent_id),
    )


def record_tournament_match(cur, tournament_id, round_id, round_number, agent1, agent2, match_result):
    """Persist the outcome of a tournament match, including metadata used by the UI."""
    raw_winner = match_result.get("raw_winner")
    normalized_winner = match_result.get("result")

    if isinstance(raw_winner, (list, tuple)) and raw_winner:
        index = raw_winner[0]
        if index in (0, 1):
            normalized_winner = f"agent{index + 1}"
    elif raw_winner is None and match_result.get("winner_agent_id") is None:
        normalized_winner = normalized_winner or "draw"

    metadata = {
        "agent1": {
            "group": agent1["groupname"],
            "name": agent1["agent_name"],
        },
        "winner": match_result["winner_label"],
        "raw_winner": raw_winner,  # Preserve engine-native outcome for debugging/audit trails.
        "normalized_winner": normalized_winner,
    }
    agent2_id = None
    agent2_score = 0
    if agent2 is not None:
        metadata["agent2"] = {
            "group": agent2["groupname"],
            "name": agent2["agent_name"],
        }
        agent2_id = agent2["agent_id"]
        agent2_score = match_result["agent2_score"]
    else:
        metadata["agent2"] = None

    if "decision" in match_result:
        metadata["decision"] = match_result["decision"]  # Indicates whether advancement was regulation, bye, or tiebreak.
    if "advancing_agent_id" in match_result:
        metadata["advancing_agent_id"] = match_result["advancing_agent_id"]  # Explicitly records who moved on to the next round.

        advancing_agent = agent1
        if agent2 is not None and match_result["advancing_agent_id"] == agent2["agent_id"]:
            advancing_agent = agent2
        metadata["advancing_agent_name"] = advancing_agent["agent_name"]

    cur.execute(
        """
        INSERT INTO tournament_matches (
            tournament_id,
            round_id,
            round_number,
            agent1_id,
            agent2_id,
            agent1_score,
            agent2_score,
            result,
            winner_agent_id,
            metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING tournament_match_id
        """,
        (
            tournament_id,
            round_id,
            round_number,
            agent1["agent_id"],
            agent2_id,
            match_result["agent1_score"],
            agent2_score,
            match_result["result"],
            match_result["winner_agent_id"],
            json.dumps(metadata),
        ),
    )
    return cur.fetchone()[0]

# ------ Tournament Functions Above ------ #

def load_class_from_file(filepath, class_name):
    """
    Dynamically load a class from a file.
    
    Args: 
        filepath (str): This must be the absolute/relative path of the Python file containing the class.
        class_name (str): The name of the class to get. Agents have a defined classname in the games dictionary above.
    
    Raises:
        TODO: Write extra testing code, what if the file isn't there?
    Return: 
        Class : Fetches the class object from the file that we can use and call. This is going to be used mainly for playing the games.
    """
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

def run_tests_on_group(groupname, game):
    """
    Run test games for a specific group and for a specific game. 
    This will run matches between the latest uploaded agent for the agent and all of the provided testing agents as listed in the games dictionary.

    Args:
        groupname (str)
        game (str): ID of the game, this must be one of the valid games in the games dict defined above

    Raises:
        # TODO: Check if the group exist or not. Need further error checking.
        ValueError: Game is not found in the configuration

    Returns:
        Dictionary : Returns a dictionary that contains the results of all of the matches.
    """
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

        game_instance = GameClass([GroupAgentClass(), TestAgentClass()])
        result = game_instance.play()

        if result[0] is None:
            winner_name = "Draw"
        elif result[0] == 0:
            winner_name = group_agent_name
        else:
            winner_name = test_agent_name
        
        results["matches"].append({
            "test_agent": test_agent_name,
            "winner": winner_name
        })

    return results


def run_group_vs_group(groups, game):
    """
    Run a single match between groups for a provided game.

    Args:
        groups (str) : List of group names that will be competing in the games. 
        game (str): One of the valid game ID in the games dictionary.

    Raises:
        ValueError: The game is not found in the games dictionary and is not a valid game.

    Returns:
        dictionary : Returns a dictionary with the result of the game.
    """
    if game not in games:
        raise ValueError(f"Game '{game}' not found in configuration.")
    game_info = games[game]

    # Load Game class
    game_module = __import__(game_info["module"], fromlist=["Game"])
    GameClass = getattr(game_module, "Game")

    # Fetch agents from each group
    agents_data = []
    for group in groups:
        agent = fetch_latest_agent(group, game)
        if not agent:
            return {"error": f"No agent found for group: {group}"}
        agents_data.append(agent)

    agent_class_name = game_info["agent"]
    
    if len(agents_data) != game_info["gamesize"]:
        return {"error": f"Game '{game}' requires {game_info['gamesize']} players, but {len(agents_data)} agents provided."}

    # Load classes dynamically
    agent_classes = []
    for agent_data in agents_data:
        AgentClass = load_class_from_file(agent_data["file_path"], agent_class_name)
        agent_classes.append(AgentClass())
        
    # Run the match
    game_instance = GameClass(agent_classes)  # Pass list of agents
    result = game_instance.play()  # Returns [winner_index, loser_index] or similar
    
    if result is None:
        winner_group = "Draw"
        loser_group = "Draw"
    else:
        winner_index = result[0]
        loser_index = result[1]
        winner_group = f"{groups[winner_index]} ({agents_data[winner_index]['name']})"
        loser_group = f"{groups[loser_index]} ({agents_data[loser_index]['name']})"

    return {
        "groups": [{"name": group, "agent": agents_data[i]["name"]} for i, group in enumerate(groups)],
        "winner": winner_group,
        "loser": loser_group
    }

@app.route("/api/admin/assign-group", methods=["POST"])
def assign_group():
    """
    Assign a user to a group. Admin only endpoint.
    
    Request Body:
        {
            "user_id": int,
            "group_id": int | null
        }
    
    Returns:
        200: {
            "user": {
                "id": int,
                "username": string,
                "email": string,
                "role": string,
                "group_id": int | null
            }
        }
        401: {"error": "Unauthorized"}
        404: {"error": "User not found"}
    """
    # Check admin authorization
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_id = data.get("user_id")
    group_id = data.get("group_id")

    if not user_id or group_id is None:
        return jsonify({"error": "Missing fields"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
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
    """
    Upload an agent file for a specific game.
    
    Parameters:
        game: string - Game type (conn4, tictactoe)
    
    Request:
        multipart/form-data with file field
        File must be .py extension
    
    Requires:
        User must be authenticated and assigned to a group
    
    Returns:
        200: {
            "message": "File uploaded successfully",
            "agent": {
                "id": int,
                "group_id": int,
                "file_path": string,
                "game": string
            }
        }
        400: {"error": "No file part"} or {"error": "Only .py files allowed"}
        401: {"error": "Not authenticated"} or {"error": "Not in a group"}
    """
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
    
@app.route("/play/group_vs_group/<groups>/<game>", methods=["GET"])
def play_group_vs_group(groups, game):
    try:
        group_list = groups.split(',')  # Parse comma-separated groups into a list
        results = run_group_vs_group(group_list, game)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/register", methods=["POST"])
def register():
    """
    Register a new user.
    
    Request Body:
        {
            "username": string,
            "email": string,
            "password": string,
            "role": string (optional, defaults to "student")
        }
    
    Returns:
        201: {
            "user": {
                "id": int,
                "username": string,
                "email": string,
                "role": string
            }
        }
        400: {"error": "Missing fields"} or {"error": "Username or Email already exists"}
        500: {"error": error message}
    """   
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
    """Simple function that just clears the session of the user, therefore effectively logging them

    Returns:
        json : Message that the user has been successfully logged out.
    """
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/create_group", methods=["POST"])
def create_group():
    """Function that will create a new group in the database

    Returns:
        JSON : Message that the group was created successfully, with the second item being the groups object containing the group data (ID and name)
    """
    # TODO: Add feature to add the user to the newly created group.
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    groupname = data.get("groupname")
    
    if not groupname:
        return jsonify({"error": "Group name required"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO groups (groupname) VALUES (%s) RETURNING group_id;",
            (groupname,)
        )
        
        group_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        return jsonify({
            "message":"Group created successfully",
            "group": {
                "id": group_id,
                "name": groupname
            }
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
        if conn:
            conn.close()
    

@app.route("/api/me", methods=["GET"])
def me():
    """
    Get current authenticated user's data.
    
    Requires:
        User must be authenticated (valid session)
    
    Returns:
        200: {
            "user": {
                "id": int,
                "username": string,
                "email": string,
                "role": string,
                "group_id": int | null
            }
        }
        401: {"error": "Not authenticated"}
        404: {"error": "User not found"}
    """
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
    """
    Authenticate user and create session.
    
    Request Body:
        {
            "email": string,
            "password": string
        }
    
    Returns:
        200: {
            "user": {
                "id": int,
                "username": string,
                "email": string,
                "role": string,
                "group_id": int | null
            }
        }
        400: {"error": "Missing fields"}
        401: {"error": "Invalid credentials"}
    """
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
    """Get the list of all registered users.

    Returns:
        JSON : Contains a users object that has a list of all of the registered users, containing the information such as ID, username, email, role and grouping
    """
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
            
@app.route("/api/groups", methods=["GET"])
def get_groups():
    """
    Get list of all available groups.
    
    Returns:
        200: {
            "groups": [
                {
                    "group_id": int,
                    "groupname": string
                }
            ]
        }
        500: {"error": error message}
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT group_id, groupname FROM groups"
        )
        groups = cur.fetchall()
        cur.close()

        return jsonify({
            "groups": [
                {
                    "group_id": group[0],
                    "groupname": group[1]
                }
                for group in groups
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            
@app.route("/api/user/agents", methods=["GET"])
def get_user_agents():
    """
    Get list of agents uploaded by user's group.
    
    Requires:
        User must be authenticated and assigned to a group
    
    Returns:
        200: {
            "agents": [
                {
                    "id": int,
                    "name": string,
                    "game": string,
                    "file_path": string,
                    "created_at": string (ISO format)
                }
            ]
        }
        401: {"error": "Not authenticated"} or {"error": "Not in a group"}
    """
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
    """
    Get list of all agents across all groups. Admin only endpoint.
    
    Requires:
        User must be authenticated and have admin role
    
    Returns:
        200: {
            "agents": [
                {
                    "id": int,
                    "name": string,
                    "game": string,
                    "file_path": string,
                    "created_at": string (ISO format),
                    "groupname": string
                }
            ]
        }
        401: {"error": "Unauthorized"}
    """
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


# ==================== CONTEST MANAGEMENT ENDPOINTS (FR3.x) ====================

@app.route("/api/contests", methods=["POST"])
def create_contest():
    """
    FR3.1: Create a new contest between two agents.
    
    Request Body:
        {
            "name": string,
            "game": string,
            "agent1_id": int,
            "agent2_id": int,
            "auto_match": boolean (optional, for FR3.2)
        }
    
    Response:
        201: {
            "message": "Contest created successfully",
            "contest_id": int
        }
        400: {"error": "Missing required fields" | "Invalid agent IDs"}
        401: {"error": "Unauthorized"}
        500: {"error": error_message}
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    name = data.get("name")
    game = data.get("game")
    agent1_id = data.get("agent1_id")
    agent2_id = data.get("agent2_id")
    auto_match = data.get("auto_match", False)
    
    if not name or not game:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # FR3.2: Auto-matching logic - if auto_match is True, select random agents
        if auto_match:
            cur.execute("""
                SELECT agent_id FROM agents 
                WHERE game = %s 
                ORDER BY RANDOM() 
                LIMIT 2
            """, (game,))
            agents = cur.fetchall()
            if len(agents) < 2:
                return jsonify({"error": "Not enough agents for auto-matching"}), 400
            agent1_id = agents[0][0]
            agent2_id = agents[1][0]
        
        if not agent1_id or not agent2_id:
            return jsonify({"error": "Invalid agent IDs"}), 400
        
        # Verify agents exist and get their details
        cur.execute("""
            SELECT agent_id, name FROM agents 
            WHERE agent_id IN (%s, %s)
        """, (agent1_id, agent2_id))
        agents = cur.fetchall()
        
        if len(agents) != 2:
            return jsonify({"error": "One or both agents not found"}), 400
        
        # Create contest
        cur.execute("""
            INSERT INTO contests (name, game, agent1_id, agent2_id, created_by, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING contest_id
        """, (name, game, agent1_id, agent2_id, session["user_id"]))
        
        contest_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        return jsonify({
            "message": "Contest created successfully",
            "contest_id": contest_id
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/contests/<int:contest_id>/run", methods=["POST"])
def run_contest(contest_id):
    """
    FR3.3: Execute a contest and track all actions throughout the match.
    FR3.4: Update win/loss records for participating agents.
    
    Response:
        200: {
            "message": "Contest completed",
            "winner_id": int,
            "actions": [
                {
                    "move_number": int,
                    "agent_id": int,
                    "action": string,
                    "board_state": string
                }
            ]
        }
        404: {"error": "Contest not found"}
        400: {"error": "Contest already completed"}
        500: {"error": error_message}
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch contest details
        cur.execute("""
            SELECT c.contest_id, c.game, c.agent1_id, c.agent2_id, c.status,
                   a1.file_path as agent1_path, a2.file_path as agent2_path
            FROM contests c
            JOIN agents a1 ON c.agent1_id = a1.agent_id
            JOIN agents a2 ON c.agent2_id = a2.agent_id
            WHERE c.contest_id = %s
        """, (contest_id,))
        
        contest = cur.fetchone()
        if not contest:
            return jsonify({"error": "Contest not found"}), 404
        
        if contest[4] == 'completed':
            return jsonify({"error": "Contest already completed"}), 400
        
        game = contest[1]
        agent1_id = contest[2]
        agent2_id = contest[3]
        agent1_path = contest[5]
        agent2_path = contest[6]
        
        # Verify game exists in configuration
        if game not in games:
            return jsonify({"error": f"Game '{game}' not found in configuration"}), 400
        
        game_info = games[game]
        
        # Load game module and agent classes
        game_module = __import__(game_info["module"], fromlist=["Game"])
        GameClass = getattr(game_module, "Game")
        
        agent_class_name = game_info["agent"]
        Agent1Class = load_class_from_file(agent1_path, agent_class_name)
        Agent2Class = load_class_from_file(agent2_path, agent_class_name)
        
        # Create agent instances
        agent1_instance = Agent1Class()
        agent2_instance = Agent2Class()
        
        # Create game instance with NEW format (list of agents)
        agent_instances = [agent1_instance, agent2_instance]
        agent_ids = [agent1_id, agent2_id]
        game_instance = GameClass(agent_instances)
        
        # Track actions during gameplay by wrapping the play() method
        actions = []
        move_number = 0
        
        # Monkey-patch the agents' move methods to capture actions
        original_moves = [agent.move for agent in agent_instances]
        
        def create_tracked_move(agent_idx, original_move_func):
            def tracked_move(*args, **kwargs):
                move = original_move_func(*args, **kwargs)
                # Capture the action
                actions.append({
                    "move_number": len(actions),
                    "agent_id": agent_ids[agent_idx],
                    "action": str(move),
                    "board_state": str(game_instance.board.copy())
                })
                return move
            return tracked_move
        
        # Apply tracking wrappers
        for idx, agent in enumerate(agent_instances):
            agent.move = create_tracked_move(idx, original_moves[idx])
        
        # Run the game with NEW return format
        result = game_instance.play()
        
        # Determine winner from NEW format
        # result is [winner_index, loser_index] or None for draw
        winner_id = None
        
        if result is not None:
            winner_index = result[0]
            winner_id = agent_ids[winner_index]
        # If result is None, it's a draw (winner_id stays None)
        
        # Update contest status
        cur.execute("""
            UPDATE contests 
            SET status = 'completed', winner_id = %s, completed_at = CURRENT_TIMESTAMP
            WHERE contest_id = %s
        """, (winner_id, contest_id))
        
        # Save all actions to database (FR3.3)
        for action in actions:
            cur.execute("""
                INSERT INTO contest_actions (contest_id, move_number, agent_id, action_data, board_state)
                VALUES (%s, %s, %s, %s, %s)
            """, (contest_id, action["move_number"], action["agent_id"], 
                  action["action"], action["board_state"]))
        
        # Update agent records (FR3.4)
        for agent_id in [agent1_id, agent2_id]:
            # Ensure record exists
            cur.execute("""
                INSERT INTO agent_records (agent_id, wins, losses, draws)
                VALUES (%s, 0, 0, 0)
                ON CONFLICT (agent_id) DO NOTHING
            """, (agent_id,))
        
        if winner_id:
            # Update winner's wins
            cur.execute("""
                UPDATE agent_records 
                SET wins = wins + 1 
                WHERE agent_id = %s
            """, (winner_id,))
            
            # Update loser's losses
            loser_id = agent2_id if winner_id == agent1_id else agent1_id
            cur.execute("""
                UPDATE agent_records 
                SET losses = losses + 1 
                WHERE agent_id = %s
            """, (loser_id,))
        else:
            # It's a draw
            cur.execute("""
                UPDATE agent_records 
                SET draws = draws + 1 
                WHERE agent_id IN (%s, %s)
            """, (agent1_id, agent2_id))
        
        conn.commit()
        cur.close()
        
        return jsonify({
            "message": "Contest completed",
            "winner_id": winner_id,
            "actions": actions
        }), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/contests", methods=["GET"])
def get_contests():
    """
    Retrieve all contests or filter by status.
    
    Query Parameters:
        status: string (optional) - Filter by status: 'pending', 'completed', 'all'
    
    Response:
        200: {
            "contests": [
                {
                    "contest_id": int,
                    "name": string,
                    "game": string,
                    "agent1_id": int,
                    "agent1_name": string,
                    "agent2_id": int,
                    "agent2_name": string,
                    "winner_id": int,
                    "status": string,
                    "created_at": string,
                    "completed_at": string
                }
            ]
        }
        500: {"error": error_message}
    """
    status_filter = request.args.get('status', 'all')
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT c.contest_id, c.name, c.game, 
                   c.agent1_id, a1.name as agent1_name,
                   c.agent2_id, a2.name as agent2_name,
                   c.winner_id, c.status, c.created_at, c.completed_at
            FROM contests c
            JOIN agents a1 ON c.agent1_id = a1.agent_id
            JOIN agents a2 ON c.agent2_id = a2.agent_id
        """
        
        if status_filter != 'all':
            query += " WHERE c.status = %s"
            cur.execute(query + " ORDER BY c.created_at DESC", (status_filter,))
        else:
            cur.execute(query + " ORDER BY c.created_at DESC")
        
        contests = cur.fetchall()
        cur.close()
        
        return jsonify({
            "contests": [
                {
                    "contest_id": contest[0],
                    "name": contest[1],
                    "game": contest[2],
                    "agent1_id": contest[3],
                    "agent1_name": contest[4],
                    "agent2_id": contest[5],
                    "agent2_name": contest[6],
                    "winner_id": contest[7],
                    "status": contest[8],
                    "created_at": contest[9].isoformat() if contest[9] else None,
                    "completed_at": contest[10].isoformat() if contest[10] else None
                }
                for contest in contests
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/contests/<int:contest_id>", methods=["GET"])
def get_contest_details(contest_id):
    """
    Get detailed information about a specific contest including all actions.
    
    Response:
        200: {
            "contest": {
                "contest_id": int,
                "name": string,
                "game": string,
                "agent1": {"id": int, "name": string, "group": string},
                "agent2": {"id": int, "name": string, "group": string},
                "winner_id": int,
                "status": string,
                "created_at": string,
                "completed_at": string
            },
            "actions": [
                {
                    "move_number": int,
                    "agent_id": int,
                    "agent_name": string,
                    "action": string,
                    "board_state": string
                }
            ]
        }
        404: {"error": "Contest not found"}
        500: {"error": error_message}
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch contest details
        cur.execute("""
            SELECT c.contest_id, c.name, c.game,
                   c.agent1_id, a1.name as agent1_name, g1.groupname as group1,
                   c.agent2_id, a2.name as agent2_name, g2.groupname as group2,
                   c.winner_id, c.status, c.created_at, c.completed_at
            FROM contests c
            JOIN agents a1 ON c.agent1_id = a1.agent_id
            JOIN agents a2 ON c.agent2_id = a2.agent_id
            JOIN groups g1 ON a1.group_id = g1.group_id
            JOIN groups g2 ON a2.group_id = g2.group_id
            WHERE c.contest_id = %s
        """, (contest_id,))
        
        contest = cur.fetchone()
        if not contest:
            return jsonify({"error": "Contest not found"}), 404
        
        # Fetch actions
        cur.execute("""
            SELECT ca.move_number, ca.agent_id, a.name, ca.action_data, ca.board_state
            FROM contest_actions ca
            JOIN agents a ON ca.agent_id = a.agent_id
            WHERE ca.contest_id = %s
            ORDER BY ca.move_number
        """, (contest_id,))
        
        actions = cur.fetchall()
        cur.close()
        
        return jsonify({
            "contest": {
                "contest_id": contest[0],
                "name": contest[1],
                "game": contest[2],
                "agent1": {"id": contest[3], "name": contest[4], "group": contest[5]},
                "agent2": {"id": contest[6], "name": contest[7], "group": contest[8]},
                "winner_id": contest[9],
                "status": contest[10],
                "created_at": contest[11].isoformat() if contest[11] else None,
                "completed_at": contest[12].isoformat() if contest[12] else None
            },
            "actions": [
                {
                    "move_number": action[0],
                    "agent_id": action[1],
                    "agent_name": action[2],
                    "action": action[3],
                    "board_state": action[4]
                }
                for action in actions
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/agents/<int:agent_id>/record", methods=["GET"])
def get_agent_record(agent_id):
    """
    FR3.4: Get win/loss/draw record for a specific agent.
    
    Response:
        200: {
            "agent_id": int,
            "agent_name": string,
            "wins": int,
            "losses": int,
            "draws": int,
            "total_contests": int
        }
        404: {"error": "Agent not found"}
        500: {"error": error_message}
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch agent info and record
        cur.execute("""
            SELECT a.agent_id, a.name, 
                   COALESCE(ar.wins, 0) as wins,
                   COALESCE(ar.losses, 0) as losses,
                   COALESCE(ar.draws, 0) as draws
            FROM agents a
            LEFT JOIN agent_records ar ON a.agent_id = ar.agent_id
            WHERE a.agent_id = %s
        """, (agent_id,))
        
        agent = cur.fetchone()
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        
        cur.close()
        
        wins = agent[2]
        losses = agent[3]
        draws = agent[4]
        
        return jsonify({
            "agent_id": agent[0],
            "agent_name": agent[1],
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total_contests": wins + losses + draws
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route("/api/admin/tournaments", methods=["POST"])
def start_tournament():
    """
    Admin endpoint to launch a single-elimination tournament for a game.
    """
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    game = data.get("game")
    if not game:
        return jsonify({"error": "Game is required"}), 400

    name = data.get("name") or f"{game.title()} Knockout Tournament"

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        agents = fetch_latest_agents_for_game(cur, game)
        if len(agents) < 2:
            return jsonify({"error": "At least two agents are required to start a tournament"}), 400

        #total_rounds = max(1, math.ceil(math.log2(len(agents))))

        cur.execute(
            """
            INSERT INTO tournaments (name, game, rounds, status, created_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING tournament_id
            """,
            (name, game, None, "running", session.get("user_id")),
        )
        tournament_id = cur.fetchone()[0]

        standings = initialize_tournament_standings(cur, tournament_id, agents)
        bracket = [agent["agent_id"] for agent in agents]
        random.shuffle(bracket)

        round_number = 1
        while len(bracket) > 1:
            cur.execute(
                """
                INSERT INTO tournament_rounds (tournament_id, round_number)
                VALUES (%s, %s)
                RETURNING round_id
                """,
                (tournament_id, round_number),
            )
            round_id = cur.fetchone()[0]

            next_round = []

            if len(bracket) % 2 == 1: # Handle bye if odd number of agents
                bye_agent_id = bracket.pop() # last agent for bye
                bye_agent = standings[bye_agent_id]
                bye_result = {
                    "winner_agent_id": bye_agent_id,
                    "agent1_score": 1,
                    "agent2_score": 0,
                    "result": "bye",
                    "winner_label": bye_agent["agent_name"],
                    "raw_winner": "BYE",
                    "decision": "bye",
                    "advancing_agent_id": bye_agent_id,
                }
                update_standing(cur, standings, tournament_id, bye_agent_id, 1) # Win for bye
                record_tournament_match(cur, tournament_id, round_id, round_number, bye_agent, None, bye_result)
                next_round.append(bye_agent_id)

            for index in range(0, len(bracket), 2):
                agent1_id = bracket[index]
                agent2_id = bracket[index + 1]
                agent1 = standings[agent1_id]
                agent2 = standings[agent2_id]

                match_result = play_agents_match(agent1, agent2, game)
                record_payload = dict(match_result)

                winner_id = match_result["winner_agent_id"]
                decision = "regulation"  # Default outcome; adjusted below for byes/tiebreaks.

                if winner_id == agent1_id:
                    update_standing(cur, standings, tournament_id, agent1_id, 1, opponent_id=agent2_id)
                    update_standing(cur, standings, tournament_id, agent2_id, -1, opponent_id=agent1_id)
                elif winner_id == agent2_id:
                    update_standing(cur, standings, tournament_id, agent1_id, -1, opponent_id=agent2_id)
                    update_standing(cur, standings, tournament_id, agent2_id, 1, opponent_id=agent1_id)
                else:
                    decision = "tiebreak(draw)"  # No winner; choose advancement while keeping scores neutral.
                    update_standing(cur, standings, tournament_id, agent1_id, 0, opponent_id=agent2_id)
                    update_standing(cur, standings, tournament_id, agent2_id, 0, opponent_id=agent1_id)
                    winner_id = random.choice((agent1_id, agent2_id))
                    record_payload["winner_agent_id"] = winner_id
                    record_payload["result"] = "agent1" if winner_id == agent1_id else "agent2"
                    record_payload["winner_label"] = f"{standings[winner_id]['agent_name']} (tiebreak)"

                record_payload["decision"] = decision
                record_payload["advancing_agent_id"] = winner_id

                record_tournament_match(cur, tournament_id, round_id, round_number, agent1, agent2, record_payload)
                next_round.append(winner_id)

            bracket = next_round
            round_number += 1

        cur.execute(
            "UPDATE tournaments SET status = 'completed' WHERE tournament_id = %s",
            (tournament_id,),
        )
        conn.commit()

        return jsonify({"tournament_id": tournament_id}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/admin/tournaments", methods=["GET"])
def list_tournaments():
    """
    Fetch summary of all tournaments with basic info and top 3 leaderboard.
    """
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT tournament_id, name, game, rounds, status, created_at
            FROM tournaments
            ORDER BY created_at DESC
            """
        )
        tournaments = []
        for row in cur.fetchall():
            tournament_id = row[0]
            cur.execute(
                "SELECT COUNT(*) FROM tournament_rounds WHERE tournament_id = %s",
                (tournament_id,),
            )
            round_count = cur.fetchone()[0]
            cur.execute(
                """
                SELECT ts.agent_id, ts.points, ts.rounds_played,
                       COALESCE(g.groupname, 'Unknown') AS groupname,
                       COALESCE(a.name, 'Unknown') AS agent_name
                FROM tournament_standings ts
                LEFT JOIN agents a ON ts.agent_id = a.agent_id
                LEFT JOIN groups g ON a.group_id = g.group_id
                WHERE ts.tournament_id = %s
                ORDER BY ts.points DESC, ts.rounds_played DESC, groupname
                LIMIT 3
                """,
                (tournament_id,), # Fetch top 3
            )
            leaderboard = [
                {
                    "agent_id": entry[0],
                    "points": int(entry[1]) if entry[1] is not None else 0,
                    "rounds_played": entry[2],
                    "groupname": entry[3],
                    "agent_name": entry[4],
                }
                for entry in cur.fetchall()
            ]
            tournaments.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "game": row[2],
                    "rounds": row[3],
                    "status": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "completed_rounds": round_count,
                    "leaderboard": leaderboard,
                }
            )

        return jsonify({"tournaments": tournaments})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/admin/tournaments/<int:tournament_id>", methods=["GET"])
def tournament_detail(tournament_id):
    """
    Fetch full knockout bracket detail including rounds, matches, and standings.
    """
    if "role" not in session or session["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT tournament_id, name, game, rounds, status, created_at
            FROM tournaments
            WHERE tournament_id = %s
            """,
            (tournament_id,),
        )
        tournament = cur.fetchone()
        if not tournament:
            return jsonify({"error": "Tournament not found"}), 404

        cur.execute(
            """
            SELECT round_id, round_number, created_at
            FROM tournament_rounds
            WHERE tournament_id = %s
            ORDER BY round_number ASC
            """,
            (tournament_id,),
        )
        rounds = [] # Will hold all rounds with their matches
        for round_row in cur.fetchall():
            round_id, round_number, created_at = round_row
            cur.execute(
                """
                SELECT tm.tournament_match_id,
                       tm.agent1_id,
                       tm.agent2_id,
                       tm.agent1_score,
                       tm.agent2_score,
                       tm.result,
                       tm.winner_agent_id,
                       tm.metadata,
                       tm.created_at
                FROM tournament_matches tm
                WHERE tm.tournament_id = %s AND tm.round_id = %s
                ORDER BY tm.tournament_match_id
                """,
                (tournament_id, round_id),
            )
            match_rows = cur.fetchall()
            matches = []
            for match in match_rows:
                raw_metadata = match[7]
                if raw_metadata is None:
                    metadata = None
                elif isinstance(raw_metadata, str):
                    try:
                        metadata = json.loads(raw_metadata)
                    except json.JSONDecodeError:
                        metadata = raw_metadata
                else:
                    metadata = raw_metadata
                matches.append(
                    {
                        "id": match[0],
                        "agent1_id": match[1],
                        "agent2_id": match[2],
                        "agent1_score": int(match[3]) if match[3] is not None else 0,
                        "agent2_score": int(match[4]) if match[4] is not None else 0,
                        "result": match[5],
                        "winner_agent_id": match[6],
                        "metadata": metadata,
                        "created_at": match[8].isoformat() if match[8] else None,
                    }
                )
            rounds.append(
                {
                    "round_id": round_id,
                    "round_number": round_number,
                    "created_at": created_at.isoformat() if created_at else None,
                    "matches": matches,
                }
            )

        cur.execute(
            """
            SELECT ts.agent_id,
                   ts.points,
                   ts.rounds_played,
                   COALESCE(g.groupname, 'Unknown') AS groupname,
                   COALESCE(a.name, 'Unknown') AS agent_name
            FROM tournament_standings ts
            LEFT JOIN agents a ON ts.agent_id = a.agent_id
            LEFT JOIN groups g ON a.group_id = g.group_id
            WHERE ts.tournament_id = %s
            ORDER BY ts.points DESC, ts.rounds_played DESC, groupname
            """,
            (tournament_id,),
        )
        standings = [
            {
                "agent_id": row[0],
                "points": int(row[1]) if row[1] is not None else 0,
                "rounds_played": row[2],
                "groupname": row[3],
                "agent_name": row[4],
            }
            for row in cur.fetchall()
        ]

        return jsonify(
            {
                "tournament": {
                    "id": tournament[0],
                    "name": tournament[1],
                    "game": tournament[2],
                    "rounds": tournament[3],
                    "status": tournament[4],
                    "created_at": tournament[5].isoformat() if tournament[5] else None,
                },
                "rounds": rounds,
                "standings": standings,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
