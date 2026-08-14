from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Task
from datetime import datetime
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

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///preday.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app);

CORS(app, origins=FRONTEND_URLS)

def require_token(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        token = request.headers.get("Authorization")
        
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized Access"}), 401
        
        return f(*args,**kwargs)
    
    return decorated_function



@app.route("/innit")
def innit_db():
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
        user = User(
            username=username,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "user created successfully"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Username already exist"}), 400
    

@app.route("/users", methods=["GET"])
@require_token
def users():
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "username": user.username
        }
        for user in users
    ])


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "enter valif info"}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    user = User.query.filter_by(
        username=username,
        password=hashed_password
    ).first()
        
    
    if user:
        return jsonify({"message": f"Welcome {username}"}), 200
    else:
        return jsonify({"error": "user not found"}), 401
    
    
@app.route("/task", methods=["GET"])
def get_task():
    username = request.args.get("username")
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 400
    return jsonify([
        {
            "id": task.id,
            "task":task.task,
            "description": task.description,
            "date": task.date.isoformat() if task.date else None
        }
        for task in user.tasks
    ]), 200
    
    
@app.route("/task", methods=["POST"])
def post_task():
    data = request.get_json()
    username = data.get("username")
    task_name = data.get("task")
    description = data.get("description")
    date = data.get("date")
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 400
    
    if date:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    
    new_task = Task(
        task=task_name,
        description=description,
        date=date,
        user=user
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({"message": "task added successfully"}), 201
    
   
@app.route("/task", methods=["DELETE"])
def delete_task():
    data = request.get_json()
    username = data.get("username")
    id = data.get("id")
        
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "user not found"}), 400
    
    task =  Task.query.filter_by(
        id=id,
        user_id=user.id
    ).first()
    
    if not task:
        return jsonify({"error": "id not found"}), 400
    
    db.session.delete(task);
    db.session.commit()
    
    return jsonify({
        "message": "task deleted successfully"
    }), 200
        
       
@app.route("/task", methods=["PUT"])
def edit_task():
    data = request.get_json()
    username = data.get("username")
    id = data.get("id")
    user = User.query.filter_by(
        username=username
    ).first()
    
    if not user:
        return jsonify({"error": "user not found"}), 400
    
    task = Task.query.filter_by(
        id=id,
        user_id=user.id
    ).first()
    
    if not task:
        return jsonify({"error": "task not found"}), 404
    
    task.task = data.get("task")
    task.description = data.get("description")
    task.date = data.get("date")
    
    db.session.commit()
    
    return jsonify({
        "message": "task edited successfully"
    }), 200
    

with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True);