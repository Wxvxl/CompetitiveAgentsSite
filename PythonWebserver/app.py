# app.py
from flask import Flask

# Create a Flask application instance
app = Flask(__name__)

# Define a route and a view function
@app.route('/')
def hello_world():
    return 'Hello, World!'

