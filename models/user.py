from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Use a separate db instance that will be initialized by the main app
db = SQLAlchemy()

class User(db.Model):
    """User model for government employees and citizens"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True)
    department = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default='user')  # admin, employee, citizen
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'