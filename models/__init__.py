"""
Database models for GOFAP - Government Operations and Financial Accounting Platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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

class Department(db.Model):
    """Government department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    budget_allocated = db.Column(db.Numeric(15, 2), default=0.00)
    budget_spent = db.Column(db.Numeric(15, 2), default=0.00)
    description = db.Column(db.Text)
    head_of_department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Procurement(db.Model):
    """Procurement and expense tracking"""
    __tablename__ = 'procurement'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(20), unique=True, nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    vendor_id = db.Column(db.String(20))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    category = db.Column(db.String(50))  # supplies, services, equipment, etc.
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='requested')  # requested, approved, ordered, received, paid
    
    # Approval workflow
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Procurement {self.po_number}>'