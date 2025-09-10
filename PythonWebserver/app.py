from flask import Flask, request, jsonify, session
from models import SessionLocal, User, Agent
from sqlalchemy.exc import IntegrityError
import bcrypt
from flask_cors import CORS
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

if __name__ == "__main__":
    app.run(debug=True)