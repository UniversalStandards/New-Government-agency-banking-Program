"""Database models for GOFAP (Government Operations and Financial Accounting Platform)."""

from datetime import datetime
from enum import Enum as PyEnum
from main import db
from sqlalchemy import Enum, Text, DateTime, Boolean, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship


class UserRole(PyEnum):
    """User role enumeration."""
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"
    CITIZEN = "citizen"


class TransactionType(PyEnum):
    """Transaction type enumeration."""
    PAYMENT = "payment"
    PAYROLL = "payroll"
    REIMBURSEMENT = "reimbursement"
    TAX_COLLECTION = "tax_collection"
    UTILITY_PAYMENT = "utility_payment"
    TRANSFER = "transfer"


class TransactionStatus(PyEnum):
    """Transaction status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(db.Model):
    """User model for employees, contractors, and citizens."""
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False, index=True)
    username = db.Column(String(80), unique=True, nullable=False, index=True)
    first_name = db.Column(String(80), nullable=False)
    last_name = db.Column(String(80), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.CITIZEN)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship('Account', back_populates='user', lazy='dynamic')
    transactions = relationship('Transaction', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Account(db.Model):
    """Bank account model."""
    __tablename__ = 'accounts'
    
    id = db.Column(Integer, primary_key=True)
    account_number = db.Column(String(50), unique=True, nullable=False, index=True)
    account_type = db.Column(String(20), nullable=False)  # checking, savings, payroll, etc.
    balance = db.Column(Float, default=0.0)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='accounts')
    transactions_from = relationship('Transaction', foreign_keys='Transaction.from_account_id', back_populates='from_account', lazy='dynamic')
    transactions_to = relationship('Transaction', foreign_keys='Transaction.to_account_id', back_populates='to_account', lazy='dynamic')
    
    def __repr__(self):
        return f'<Account {self.account_number}>'


class Transaction(db.Model):
    """Transaction model for all financial operations."""
    __tablename__ = 'transactions'
    
    id = db.Column(Integer, primary_key=True)
    transaction_id = db.Column(String(100), unique=True, nullable=False, index=True)
    transaction_type = db.Column(Enum(TransactionType), nullable=False)
    status = db.Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    amount = db.Column(Float, nullable=False)
    currency = db.Column(String(3), default='USD')
    description = db.Column(Text)
    extra_data = db.Column(Text)  # JSON string for additional data
    processed_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    from_account_id = db.Column(Integer, ForeignKey('accounts.id'))
    to_account_id = db.Column(Integer, ForeignKey('accounts.id'))
    
    # Relationships
    user = relationship('User', back_populates='transactions')
    from_account = relationship('Account', foreign_keys=[from_account_id], back_populates='transactions_from')
    to_account = relationship('Account', foreign_keys=[to_account_id], back_populates='transactions_to')
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'


class PayrollRecord(db.Model):
    """Payroll record model for employee payments."""
    __tablename__ = 'payroll_records'
    
    id = db.Column(Integer, primary_key=True)
    employee_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    pay_period_start = db.Column(DateTime, nullable=False)
    pay_period_end = db.Column(DateTime, nullable=False)
    gross_pay = db.Column(Float, nullable=False)
    net_pay = db.Column(Float, nullable=False)
    tax_withheld = db.Column(Float, default=0.0)
    benefits_deduction = db.Column(Float, default=0.0)
    other_deductions = db.Column(Float, default=0.0)
    processed = db.Column(Boolean, default=False)
    processed_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship('User', backref='payroll_records')
    
    def __repr__(self):
        return f'<PayrollRecord {self.employee_id} - {self.pay_period_start}>'


class Budget(db.Model):
    """Budget model for departmental budgets and tracking."""
    __tablename__ = 'budgets'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    department = db.Column(String(100), nullable=False)
    fiscal_year = db.Column(Integer, nullable=False)
    allocated_amount = db.Column(Float, nullable=False)
    spent_amount = db.Column(Float, default=0.0)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Budget {self.name} - {self.fiscal_year}>'


class UtilityPayment(db.Model):
    """Utility payment model for citizen services."""
    __tablename__ = 'utility_payments'
    
    id = db.Column(Integer, primary_key=True)
    citizen_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    utility_type = db.Column(String(50), nullable=False)  # water, electric, gas, etc.
    account_number = db.Column(String(100), nullable=False)
    amount_due = db.Column(Float, nullable=False)
    amount_paid = db.Column(Float)
    due_date = db.Column(DateTime, nullable=False)
    paid_date = db.Column(DateTime)
    is_paid = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    citizen = relationship('User', backref='utility_payments')
    
    def __repr__(self):
        return f'<UtilityPayment {self.utility_type} - {self.account_number}>'