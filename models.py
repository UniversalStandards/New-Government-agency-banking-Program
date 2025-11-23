"""
Database models for GOFAP (Government Operations and Financial Accounting Platform).
"""

import uuid
from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

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

    __tablename__ = "users"

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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login = db.Column(db.DateTime)

    # Relationships
    accounts = db.relationship("Account", backref="owner", lazy=True)
    transactions = db.relationship("Transaction", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "department": self.department,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class Account(db.Model):
    """Account model for financial accounts."""

    __tablename__ = "accounts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    external_id = db.Column(
        db.String(100)
    )  # ID from external service (Stripe, Modern Treasury)
    external_service = db.Column(db.String(50))  # 'stripe', 'modern_treasury', etc.
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default="USD")
    routing_number = db.Column(db.String(20))
    account_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    transactions = db.relationship("Transaction", backref="account", lazy=True)

    def to_dict(self):
        """Convert account to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_name": self.account_name,
            "account_type": self.account_type.value,
            "external_id": self.external_id,
            "external_service": self.external_service,
            "balance": float(self.balance),
            "currency": self.currency,
            "routing_number": self.routing_number,
            "account_number": self.account_number,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Transaction(db.Model):
    """Transaction model for financial transactions."""

    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey("accounts.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    external_id = db.Column(db.String(100))  # ID from external service
    external_service = db.Column(db.String(50))
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default="USD")
    description = db.Column(db.Text)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    reference_number = db.Column(db.String(100))
    transaction_metadata = db.Column(db.JSON)  # Additional transaction data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    processed_at = db.Column(db.DateTime)

    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "user_id": self.user_id,
            "external_id": self.external_id,
            "external_service": self.external_service,
            "transaction_type": self.transaction_type.value,
            "amount": float(self.amount),
            "currency": self.currency,
            "description": self.description,
            "status": self.status.value,
            "reference_number": self.reference_number,
            "transaction_metadata": self.transaction_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
        }


class Budget(db.Model):
    """Budget model for financial planning."""

    __tablename__ = "budgets"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    fiscal_year = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100))
    total_budget = db.Column(db.Numeric(15, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default="USD")
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    budget_items = db.relationship(
        "BudgetItem", backref="budget", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert budget to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "fiscal_year": self.fiscal_year,
            "department": self.department,
            "total_budget": float(self.total_budget),
            "spent_amount": float(self.spent_amount),
            "remaining_amount": float(self.total_budget - self.spent_amount),
            "currency": self.currency,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BudgetItem(db.Model):
    """Budget item model for detailed budget breakdown."""

    __tablename__ = "budget_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = db.Column(db.String(36), db.ForeignKey("budgets.id"), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    allocated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(15, 2), default=0.00)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        """Convert budget item to dictionary."""
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "allocated_amount": float(self.allocated_amount),
            "spent_amount": float(self.spent_amount),
            "remaining_amount": float(self.allocated_amount - self.spent_amount),
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """Audit log model for tracking system changes."""

    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
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
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Department(db.Model):
    """Department model for government departments."""

    __tablename__ = "departments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    budget_allocated = db.Column(db.Numeric(15, 2), default=0.00)
    budget_spent = db.Column(db.Numeric(15, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def budget_remaining(self):
        """Calculate remaining budget."""
        return self.budget_allocated - self.budget_spent

    def to_dict(self):
        """Convert department to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "budget_allocated": (
                float(self.budget_allocated) if self.budget_allocated else 0
            ),
            "budget_spent": float(self.budget_spent) if self.budget_spent else 0,
            "budget_remaining": (
                float(self.budget_remaining) if self.budget_remaining else 0
            ),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# HR Management Enums
class EmploymentStatus(Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RETIRED = "retired"
    SUSPENDED = "suspended"


class LeaveType(Enum):
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"


class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# Project Management Enums
class ProjectStatus(Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Procurement Enums
class PurchaseOrderStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class VendorStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# ============= HR Management Models =============


class Employee(db.Model):
    """Employee model for HR management."""

    __tablename__ = "employees"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.String(36), db.ForeignKey("departments.id"))
    job_title = db.Column(db.String(100), nullable=False)
    employment_status = db.Column(
        db.Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE
    )
    hire_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date)
    salary = db.Column(db.Numeric(15, 2))
    supervisor_id = db.Column(db.String(36), db.ForeignKey("employees.id"))
    emergency_contact = db.Column(db.JSON)  # {name, phone, relationship}
    benefits = db.Column(db.JSON)  # Health, dental, retirement, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    leave_requests = db.relationship("LeaveRequest", backref="employee", lazy=True)
    performance_reviews = db.relationship(
        "PerformanceReview", backref="employee", lazy=True
    )
    payroll_records = db.relationship("PayrollRecord", backref="employee", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "employee_number": self.employee_number,
            "department_id": self.department_id,
            "job_title": self.job_title,
            "employment_status": self.employment_status.value,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "termination_date": (
                self.termination_date.isoformat() if self.termination_date else None
            ),
            "salary": float(self.salary) if self.salary else None,
            "supervisor_id": self.supervisor_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LeaveRequest(db.Model):
    """Leave request model for employee time off."""

    __tablename__ = "leave_requests"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(
        db.String(36), db.ForeignKey("employees.id"), nullable=False
    )
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum(LeaveStatus), default=LeaveStatus.PENDING)
    approved_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    approval_date = db.Column(db.DateTime)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "leave_type": self.leave_type.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "days_requested": self.days_requested,
            "reason": self.reason,
            "status": self.status.value,
            "approved_by": self.approved_by,
            "approval_date": (
                self.approval_date.isoformat() if self.approval_date else None
            ),
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PerformanceReview(db.Model):
    """Performance review model for employee evaluations."""

    __tablename__ = "performance_reviews"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(
        db.String(36), db.ForeignKey("employees.id"), nullable=False
    )
    reviewer_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 scale
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals = db.Column(db.Text)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "reviewer_id": self.reviewer_id,
            "review_period_start": (
                self.review_period_start.isoformat()
                if self.review_period_start
                else None
            ),
            "review_period_end": (
                self.review_period_end.isoformat() if self.review_period_end else None
            ),
            "rating": self.rating,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "goals": self.goals,
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PayrollRecord(db.Model):
    """Payroll record model for employee payments."""

    __tablename__ = "payroll_records"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(
        db.String(36), db.ForeignKey("employees.id"), nullable=False
    )
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    gross_pay = db.Column(db.Numeric(15, 2), nullable=False)
    deductions = db.Column(db.Numeric(15, 2), default=0.00)
    net_pay = db.Column(db.Numeric(15, 2), nullable=False)
    tax_withheld = db.Column(db.Numeric(15, 2), default=0.00)
    benefits_deduction = db.Column(db.Numeric(15, 2), default=0.00)
    payment_method = db.Column(db.String(50))  # Direct deposit, check, etc.
    payment_date = db.Column(db.Date)
    transaction_id = db.Column(db.String(36), db.ForeignKey("transactions.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "pay_period_start": (
                self.pay_period_start.isoformat() if self.pay_period_start else None
            ),
            "pay_period_end": (
                self.pay_period_end.isoformat() if self.pay_period_end else None
            ),
            "gross_pay": float(self.gross_pay),
            "deductions": float(self.deductions),
            "net_pay": float(self.net_pay),
            "tax_withheld": float(self.tax_withheld),
            "benefits_deduction": float(self.benefits_deduction),
            "payment_method": self.payment_method,
            "payment_date": (
                self.payment_date.isoformat() if self.payment_date else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============= Project Management Models =============


class Project(db.Model):
    """Project model for project management."""

    __tablename__ = "projects"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    department_id = db.Column(db.String(36), db.ForeignKey("departments.id"))
    project_manager_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2), default=0.00)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    completion_percentage = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tasks = db.relationship(
        "Task", backref="project", lazy=True, cascade="all, delete-orphan"
    )
    milestones = db.relationship(
        "Milestone", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "department_id": self.department_id,
            "project_manager_id": self.project_manager_id,
            "status": self.status.value,
            "budget": float(self.budget) if self.budget else None,
            "actual_cost": float(self.actual_cost),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "completion_percentage": self.completion_percentage,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Task(db.Model):
    """Task model for project tasks."""

    __tablename__ = "tasks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.String(36), db.ForeignKey("users.id"))
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    estimated_hours = db.Column(db.Numeric(10, 2))
    actual_hours = db.Column(db.Numeric(10, 2), default=0.00)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    parent_task_id = db.Column(db.String(36), db.ForeignKey("tasks.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    subtasks = db.relationship(
        "Task", backref=db.backref("parent_task", remote_side=[id]), lazy=True
    )
    time_entries = db.relationship("TimeEntry", backref="task", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "priority": self.priority.value,
            "estimated_hours": (
                float(self.estimated_hours) if self.estimated_hours else None
            ),
            "actual_hours": float(self.actual_hours),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_date": (
                self.completed_date.isoformat() if self.completed_date else None
            ),
            "parent_task_id": self.parent_task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Milestone(db.Model):
    """Milestone model for project milestones."""

    __tablename__ = "milestones"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_date": (
                self.completed_date.isoformat() if self.completed_date else None
            ),
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TimeEntry(db.Model):
    """Time entry model for time tracking."""

    __tablename__ = "time_entries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    hours = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "hours": float(self.hours),
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============= Procurement Models =============


class Vendor(db.Model):
    """Vendor model for supplier management."""

    __tablename__ = "vendors"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    vendor_code = db.Column(db.String(20), unique=True, nullable=False)
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    status = db.Column(db.Enum(VendorStatus), default=VendorStatus.ACTIVE)
    payment_terms = db.Column(db.String(50))
    rating = db.Column(db.Integer)  # 1-5 scale
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    purchase_orders = db.relationship("PurchaseOrder", backref="vendor", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "vendor_code": self.vendor_code,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "tax_id": self.tax_id,
            "status": self.status.value,
            "payment_terms": self.payment_terms,
            "rating": self.rating,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PurchaseOrder(db.Model):
    """Purchase order model for procurement."""

    __tablename__ = "purchase_orders"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendors.id"), nullable=False)
    department_id = db.Column(db.String(36), db.ForeignKey("departments.id"))
    requester_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    approver_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    status = db.Column(db.Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(15, 2), default=0.00)
    shipping_cost = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default="USD")
    notes = db.Column(db.Text)
    budget_id = db.Column(db.String(36), db.ForeignKey("budgets.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    items = db.relationship(
        "PurchaseOrderItem",
        backref="purchase_order",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "po_number": self.po_number,
            "vendor_id": self.vendor_id,
            "department_id": self.department_id,
            "requester_id": self.requester_id,
            "approver_id": self.approver_id,
            "status": self.status.value,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "expected_delivery_date": (
                self.expected_delivery_date.isoformat()
                if self.expected_delivery_date
                else None
            ),
            "actual_delivery_date": (
                self.actual_delivery_date.isoformat()
                if self.actual_delivery_date
                else None
            ),
            "total_amount": float(self.total_amount),
            "tax_amount": float(self.tax_amount),
            "shipping_cost": float(self.shipping_cost),
            "currency": self.currency,
            "notes": self.notes,
            "budget_id": self.budget_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PurchaseOrderItem(db.Model):
    """Purchase order item model for line items."""

    __tablename__ = "purchase_order_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    purchase_order_id = db.Column(
        db.String(36), db.ForeignKey("purchase_orders.id"), nullable=False
    )
    item_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    total_price = db.Column(db.Numeric(15, 2), nullable=False)
    received_quantity = db.Column(db.Integer, default=0)
    unit_of_measure = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_order_id": self.purchase_order_id,
            "item_number": self.item_number,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "total_price": float(self.total_price),
            "received_quantity": self.received_quantity,
            "unit_of_measure": self.unit_of_measure,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Requisition(db.Model):
    """Requisition model for purchase requests."""

    __tablename__ = "requisitions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requisition_number = db.Column(db.String(50), unique=True, nullable=False)
    requester_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    department_id = db.Column(db.String(36), db.ForeignKey("departments.id"))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    estimated_cost = db.Column(db.Numeric(15, 2))
    justification = db.Column(db.Text)
    status = db.Column(db.Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    approved_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    approval_date = db.Column(db.DateTime)
    purchase_order_id = db.Column(db.String(36), db.ForeignKey("purchase_orders.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "requisition_number": self.requisition_number,
            "requester_id": self.requester_id,
            "department_id": self.department_id,
            "title": self.title,
            "description": self.description,
            "estimated_cost": (
                float(self.estimated_cost) if self.estimated_cost else None
            ),
            "justification": self.justification,
            "status": self.status.value,
            "approved_by": self.approved_by,
            "approval_date": (
                self.approval_date.isoformat() if self.approval_date else None
            ),
            "purchase_order_id": self.purchase_order_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
