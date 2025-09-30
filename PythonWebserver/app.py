from flask import Flask, request, jsonify, session
from flask_cors import CORS
import importlib.util
import psycopg2
from psycopg2 import errors
import bcrypt
import os

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
    """
    Run a single match between two groups for a provided game.

    Args:
        group1 (str) : Groupname of the first group.
        group2 (str) : Groupname of the second group.
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
    
@app.route("/play/group_vs_group/<group1>/<group2>/<game>", methods=["GET"])
def play_group_vs_group(group1, group2, game):
    try:
        results = run_group_vs_group(group1, group2, game)
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
            
if __name__ == "__main__":
    app.run(debug=True)
