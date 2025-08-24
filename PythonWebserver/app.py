from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

db_name = "testdb"
def get_db_connection():
    conn = psycopg2.connect(
        dbname=db_name,       
        user="postgres",     
        password="admin", 
        host="localhost"     
    )
    return conn

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
            "code": r[3],               # code as text
        }
        for r in rows
    ]
    return jsonify(scripts)
if __name__ == "__main__":
    app.run(debug=True)