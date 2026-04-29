from flask import Flask, jsonify, request
import sqlite3
import hashlib
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

app = Flask(__name__)

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
                     username TEXT UNQIUE NOT NULL,
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
        conn.commit()
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {username}_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            task TEXT NOT NULL
            )""")
        conn.close()
        return jsonify({"message": "user created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exist"}), 400
    

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
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": f"Welcome {username}"})
    else:
        return jsonify({"error": "user not found"})
    
    
@app.route("/user/<string:username>/<string:password>/task", methods=["GET"])
def get_task(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_to_db()
    rows = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
    if rows:
        task_row = conn.execute(f"SELECT * FROM {username}_tasks").fetchall()
        conn.close()
        return jsonify([dict(row) for row in task_row]), 201
    else:
        conn.close()
        return jsonify({"error": "User not found"}), 400
    
    
@app.route("/user/<string:username>/<string:password>/task", methods=["POST"])
def post_task(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_to_db()
    rows = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
    if rows:
       data = request.get_json()
       task = data.get("task")
       conn.execute(f"INSERT INTO {username}_tasks (task) VALUES (?)", (task,))
       conn.commit()
       conn.close()
       return jsonify({"message": "task added successfully"}), 201
    else:
       conn.close()
       return jsonify({"error": "User not found"}), 400
   
@app.route("/user/<string:username>/<string:password>/task/<int:id>", methods=["DELETE"])
def delete_task(username, password, id):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = connect_to_db()
        rows = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
        if rows:
           if(conn.execute(f"SELECT * FROM {username}_tasks WHERE id=?", (id,)).fetchone()):
               conn.execute(f"DELETE FROM {username}_tasks WHERE id=?", (id,))
               conn.commit()
               conn.close()
               return jsonify({"message": "task deleted successfully"}), 201
           else:
               return jsonify({"error": "id not found"}), 400
           
        else:
           conn.close()
           return jsonify({"error": "User not found"}), 400

if __name__ == "__main__":
    with app.app_context():
        innit_db()
    app.run(debug=True);