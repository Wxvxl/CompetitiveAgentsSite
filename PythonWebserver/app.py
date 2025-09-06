from flask import Flask, request, jsonify

import psycopg2

app = Flask(__name__)
    
if __name__ == "__main__":
    app.run(debug=True)