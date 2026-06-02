from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    
    password = db.Column(
        db.String(255),
        nullable=False
    )
    
    tasks = db.relationship(
        "Task",
        backref="user",
        lazy=True
    )

class Task(db.Model):
    __tablename__ = "tasks"
    
    id = db.Column(db.Integer, primary_key=True)
    
    task = db.Column(
        db.String(500),
        nullable=False
    )
    
    description = db.Column(
        db.String(500)
    )
    
    date = db.Column(
        db.Date
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    
    