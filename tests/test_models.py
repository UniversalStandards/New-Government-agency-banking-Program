"""
Test cases for GOFAP models.
"""

import pytest
import os
import tempfile
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import models
from models import (
    db,
    User,
    Account,
    Transaction,
    Budget,
    BudgetItem,
    UserRole,
    AccountType,
    TransactionType,
    TransactionStatus,
)


@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "test-secret-key"

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.EMPLOYEE,
            department="IT",
        )
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()
        return user


def test_user_creation(sample_user):
    """Test user creation and password hashing."""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.check_password("testpassword")
    assert not sample_user.check_password("wrongpassword")
    assert sample_user.is_active == True


def test_user_to_dict(sample_user):
    """Test user serialization."""
    user_dict = sample_user.to_dict()
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert user_dict["role"] == "employee"
    assert "password_hash" not in user_dict


def test_account_creation(app, sample_user):
    """Test account creation."""
    with app.app_context():
        account = Account(
            user_id=sample_user.id,
            account_name="Test Account",
            account_type=AccountType.CHECKING,
            balance=1000.00,
            currency="USD",
        )
        db.session.add(account)
        db.session.commit()

        assert account.account_name == "Test Account"
        assert account.account_type == AccountType.CHECKING
        assert float(account.balance) == 1000.00
        assert account.user_id == sample_user.id


def test_transaction_creation(app, sample_user):
    """Test transaction creation."""
    with app.app_context():
        # Create account first
        account = Account(
            user_id=sample_user.id,
            account_name="Test Account",
            account_type=AccountType.CHECKING,
            balance=1000.00,
        )
        db.session.add(account)
        db.session.commit()

        # Create transaction
        transaction = Transaction(
            account_id=account.id,
            user_id=sample_user.id,
            transaction_type=TransactionType.DEPOSIT,
            amount=500.00,
            description="Test deposit",
        )
        db.session.add(transaction)
        db.session.commit()

        assert transaction.amount == 500.00
        assert transaction.transaction_type == TransactionType.DEPOSIT
        assert transaction.status == TransactionStatus.PENDING


def test_budget_creation(app, sample_user):
    """Test budget creation."""
    with app.app_context():
        budget = Budget(
            name="Test Budget",
            description="Test budget description",
            fiscal_year=2024,
            department="IT",
            total_budget=100000.00,
            created_by=sample_user.id,
        )
        db.session.add(budget)
        db.session.commit()

        assert budget.name == "Test Budget"
        assert budget.fiscal_year == 2024
        assert float(budget.total_budget) == 100000.00
        assert budget.created_by == sample_user.id


def test_budget_item_creation(app, sample_user):
    """Test budget item creation."""
    with app.app_context():
        # Create budget first
        budget = Budget(
            name="Test Budget",
            fiscal_year=2024,
            total_budget=100000.00,
            created_by=sample_user.id,
        )
        db.session.add(budget)
        db.session.commit()

        # Create budget item
        budget_item = BudgetItem(
            budget_id=budget.id,
            category="Equipment",
            subcategory="Computers",
            allocated_amount=50000.00,
            description="Computer equipment purchase",
        )
        db.session.add(budget_item)
        db.session.commit()

        assert budget_item.category == "Equipment"
        assert budget_item.subcategory == "Computers"
        assert float(budget_item.allocated_amount) == 50000.00
        assert budget_item.budget_id == budget.id


def test_user_roles():
    """Test user role enumeration."""
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.EMPLOYEE.value == "employee"
    assert UserRole.TREASURER.value == "treasurer"


def test_account_types():
    """Test account type enumeration."""
    assert AccountType.CHECKING.value == "checking"
    assert AccountType.SAVINGS.value == "savings"
    assert AccountType.CREDIT.value == "credit"


def test_transaction_types():
    """Test transaction type enumeration."""
    assert TransactionType.DEPOSIT.value == "deposit"
    assert TransactionType.WITHDRAWAL.value == "withdrawal"
    assert TransactionType.TRANSFER.value == "transfer"


def test_transaction_statuses():
    """Test transaction status enumeration."""
    assert TransactionStatus.PENDING.value == "pending"
    assert TransactionStatus.COMPLETED.value == "completed"
    assert TransactionStatus.FAILED.value == "failed"
