from flask import Flask, jsonify, request
import sqlite3
import hashlib
import os
from functools import wraps
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

FRONTEND_URLS = [
    url.strip()
    for url in os.getenv("FRONTEND_URL", "").split(",")
    if url.strip()
]

app = Flask(__name__)

CORS(app, origins=FRONTEND_URLS)

def require_token(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        token = request.headers.get("Authorization")
        
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized Access"}), 401
        
        return f(*args,**kwargs)
    
    return decorated_function

def connect_to_db():
    conn = sqlite3.connect("preday.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/innit")
def innit_db():
    conn = connect_to_db()
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS users(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL
                 )
                 """)
    conn.commit()
    conn.close()
    return jsonify({"message": "database intialized successfully"}), 201

@app.route("/")
def home():
    home = "This server is built for a personal Project called PreDay by @tejashhxd. It's available in Github"
    return jsonify(home)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "enter Proper Credentials"})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        conn = connect_to_db()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {username}_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            task TEXT NOT NULL,
            description TEXT, 
            date DATE
            )""")
        conn.commit()
        return jsonify({"message": "user created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exist"}), 400
    finally:
        conn.close()
    

@app.route("/users", methods=["GET"])
@require_token
def users():
    conn = connect_to_db()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "enter valif info"}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_to_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
    finally:
        conn.close()
    
    if user:
        return jsonify({"message": f"Welcome {username}"})
    else:
        return jsonify({"error": "user not found"})
    
    
@app.route("/task", methods=["GET"])
def get_task():
    username = request.args.get("username")
    conn = connect_to_db()
    rows = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if rows:
        task_row = conn.execute(f"SELECT * FROM {username}_tasks").fetchall()
        conn.close()
        return jsonify([dict(row) for row in task_row]), 200
    else:
        conn.close()
        return jsonify({"error": "User not found"}), 400
    
    
@app.route("/task", methods=["POST"])
def post_task():
    data = request.get_json()
    username = data.get("username")
    task = data.get("task")
    description = data.get("description")
    date = data.get("date")
    conn = connect_to_db()
    try:
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if rows:
            conn.execute(f"INSERT INTO {username}_tasks (task, description, date) VALUES (?, ?, ?)", (task,description,date))
            conn.commit()
            return jsonify({"message": "task added successfully"}), 201
        else:
            return jsonify({"error": "User not found"}), 400
        
    finally:
        conn.close()
    
   
@app.route("/task", methods=["DELETE"])
def delete_task():
        data = request.get_json()
        username = data.get("username")
        id = data.get("id")
        conn = connect_to_db()
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if rows:
           if(conn.execute(f"SELECT * FROM {username}_tasks WHERE id=?", (id,)).fetchone()):
               conn.execute(f"DELETE FROM {username}_tasks WHERE id=?", (id,))
               conn.commit()
               conn.close()
               return jsonify({"message": "task deleted successfully"}), 200
           else:
               return jsonify({"error": "id not found"}), 400
           
        else:
           conn.close()
           return jsonify({"error": "User not found"}), 400
       
@app.route("/task", methods=["PUT"])
def edit_task():
    data = request.get_json()
    task = data.get("task")
    description = data.get("description")
    date = data.get("date")
    username = data.get("username")
    id = data.get("id")
    conn = connect_to_db()
    try:
        conn.execute(f"UPDATE {username}_tasks SET task=?, description=?, date=? WHERE id=?", (task, description, date, id))
        conn.commit()
        conn.close()
        return jsonify({"message": "task edited succesfully"}), 201
    finally:
        conn.close()
        

with app.app_context():
        innit_db()

if __name__ == "__main__":
    
    app.run(debug=True);