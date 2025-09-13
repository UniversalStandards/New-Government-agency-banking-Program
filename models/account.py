from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Use a separate db instance that will be initialized by the main app
db = SQLAlchemy()

class Account(db.Model):
    """Bank account model"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # checking, savings, credit
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    routing_number = db.Column(db.String(9))
    bank_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, frozen, closed
    
    # External service IDs
    modern_treasury_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def __repr__(self):
        return f'<Account {self.account_number}>'