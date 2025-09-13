from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Use a separate db instance that will be initialized by the main app
db = SQLAlchemy()

class Transaction(db.Model):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    transaction_type = db.Column(db.String(20), nullable=False)  # debit, credit, transfer
    category = db.Column(db.String(50))  # payroll, procurement, utilities, etc.
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    
    # External service transaction IDs
    stripe_payment_intent_id = db.Column(db.String(100))
    modern_treasury_payment_id = db.Column(db.String(100))
    
    # Foreign keys
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'