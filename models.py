"""
Database models for GOFAP (Government Operations and Financial Accounting Platform).
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid

db = SQLAlchemy()

class UserRole(Enum):
    ADMIN = "admin"
    TREASURER = "treasurer"
    ACCOUNTANT = "accountant"
    HR_MANAGER = "hr_manager"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"
    CITIZEN = "citizen"

class AccountType(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    DEBIT = "debit"
    EXTERNAL = "external"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    PAYROLL = "payroll"
    REFUND = "refund"
    FEE = "fee"

class TransactionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    accounts = db.relationship('Account', backref='owner', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Account(db.Model):
    """Account model for financial accounts."""
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    external_id = db.Column(db.String(100))  # ID from external service (Stripe, Modern Treasury)
    external_service = db.Column(db.String(50))  # 'stripe', 'modern_treasury', etc.
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    routing_number = db.Column(db.String(20))
    account_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def to_dict(self):
        """Convert account to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_name': self.account_name,
            'account_type': self.account_type.value,
            'external_id': self.external_id,
            'external_service': self.external_service,
            'balance': float(self.balance),
            'currency': self.currency,
            'routing_number': self.routing_number,
            'account_number': self.account_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    """Transaction model for financial transactions."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    external_id = db.Column(db.String(100))  # ID from external service
    external_service = db.Column(db.String(50))
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    description = db.Column(db.Text)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    reference_number = db.Column(db.String(100))
    metadata = db.Column(db.JSON)  # Additional transaction data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'external_id': self.external_id,
            'external_service': self.external_service,
            'transaction_type': self.transaction_type.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'description': self.description,
            'status': self.status.value,
            'reference_number': self.reference_number,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class Budget(db.Model):
    """Budget model for financial planning."""
    __tablename__ = 'budgets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    fiscal_year = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100))
    total_budget = db.Column(db.Numeric(15, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    budget_items = db.relationship('BudgetItem', backref='budget', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert budget to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'fiscal_year': self.fiscal_year,
            'department': self.department,
            'total_budget': float(self.total_budget),
            'spent_amount': float(self.spent_amount),
            'remaining_amount': float(self.total_budget - self.spent_amount),
            'currency': self.currency,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BudgetItem(db.Model):
    """Budget item model for detailed budget breakdown."""
    __tablename__ = 'budget_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    allocated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(15, 2), default=0.00)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert budget item to dictionary."""
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'allocated_amount': float(self.allocated_amount),
            'spent_amount': float(self.spent_amount),
            'remaining_amount': float(self.allocated_amount - self.spent_amount),
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AuditLog(db.Model):
    """Audit log model for tracking system changes."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(36), nullable=False)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }