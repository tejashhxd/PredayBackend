from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Task
from datetime import datetime
import hashlib
import os
from functools import wraps
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies

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
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True #false for localSite and True for deployement
app.config["JWT_COOKIE_HTTPONLY"] = False #false for localSite and True for deployement
app.config["JWT_COOKIE_SAMESITE"] = "none"

jwt = JWTManager(app)

db.init_app(app);

CORS(
    app,
    supports_credentials=True,
    origins=FRONTEND_URLS
)

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
        return jsonify({"error": "enter valid info"}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    user = User.query.filter_by(
        username=username,
        password=hashed_password
    ).first()
    
    if user:
        if user.password != hashed_password:
            return jsonify({"error": "invalid username or password"}), 401
        
        access_token = create_access_token(
            identity=str(user.id)
        )
        
        response = jsonify({
            "message": "Login successful"
        })
        
        set_access_cookies(response, access_token)
        
        return response, 200
    
    else:
        return jsonify({"error": "user not found"}), 401
    
    

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({
        "message": "Logged out successfully"
    })
    
    unset_jwt_cookies(response)
    
    return response, 200


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    
    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200
    
    
    
@app.route("/task", methods=["GET"])
@jwt_required()
def get_task():
    user_id = get_jwt_identity()
    
    user = User.query.filter_by(id=user_id).first()
    
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
@jwt_required()
def post_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    task_name = data.get("task")
    description = data.get("description")
    date = data.get("date")
    
    user = User.query.filter_by(id=user_id).first()
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
@jwt_required()
def delete_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    id = data.get("id")
        
    user = User.query.filter_by(id=user_id).first()
    
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
@jwt_required()
def edit_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    id = data.get("id")
    user = User.query.filter_by(
        id=user_id
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
    task.date = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
    
    db.session.commit()
    
    return jsonify({
        "message": "task edited successfully"
    }), 200
    

with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True);