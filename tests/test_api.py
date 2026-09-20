"""Test cases for current GOFAP API endpoints."""

import os

import pytest
from flask import Flask
from flask_login import LoginManager

from api import api_bp
from models import (Account, AccountType, Transaction, TransactionType, User,
                    UserRole, db)


@pytest.fixture
def app():
    """Create a test Flask application with the current API blueprint."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    app.register_blueprint(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    with app.app_context():
        db.create_all()

        admin_user = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            department="Finance",
        )
        admin_user.set_password("admin123")

        regular_user = User(
            username="user",
            email="user@example.com",
            first_name="Regular",
            last_name="User",
            role=UserRole.USER,
            department="Finance",
        )
        regular_user.set_password("user123")

        db.session.add_all([admin_user, regular_user])
        db.session.commit()

        test_account = Account(
            account_name="Test Account",
            account_type=AccountType.CHECKING,
            balance=1000.00,
            currency="USD",
            user_id=regular_user.id,
        )
        db.session.add(test_account)
        db.session.commit()

        app.config["TEST_ADMIN_ID"] = admin_user.id
        app.config["TEST_USER_ID"] = regular_user.id
        app.config["TEST_ACCOUNT_ID"] = test_account.id

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def admin_client(client, app):
    """Create an authenticated admin client."""
    with client.session_transaction() as session:
        session["_user_id"] = app.config["TEST_ADMIN_ID"]
        session["_fresh"] = True
    return client


@pytest.fixture
def user_client(client, app):
    """Create an authenticated regular user client."""
    with client.session_transaction() as session:
        session["_user_id"] = app.config["TEST_USER_ID"]
        session["_fresh"] = True
    return client


def test_health_check(client):
    """The API health check should be public and healthy."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_get_accounts_returns_authenticated_user_accounts(user_client, app):
    """Authenticated users should receive only their active accounts."""
    response = user_client.get("/api/v1/accounts")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["data"][0]["id"] == app.config["TEST_ACCOUNT_ID"]


def test_create_account_creates_current_user_account(user_client):
    """Authenticated users should be able to create accounts for themselves."""
    response = user_client.post(
        "/api/v1/accounts",
        json={
            "account_name": "New Savings Account",
            "account_type": "savings",
            "currency": "USD",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["account_name"] == "New Savings Account"
    assert data["data"]["account_type"] == "savings"


def test_get_transactions_returns_current_user_transactions(user_client, app):
    """Transaction listing should be scoped to the authenticated user."""
    with app.app_context():
        transaction = Transaction(
            account_id=app.config["TEST_ACCOUNT_ID"],
            user_id=app.config["TEST_USER_ID"],
            transaction_type=TransactionType.DEPOSIT,
            amount=25.00,
            description="Seed transaction",
        )
        db.session.add(transaction)
        db.session.commit()

    response = user_client.get("/api/v1/transactions")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["pagination"]["total"] == 1
    assert data["data"][0]["description"] == "Seed transaction"


def test_create_transaction_updates_balance(user_client, app):
    """Creating a transaction should persist it and update the account balance."""
    response = user_client.post(
        "/api/v1/transactions",
        json={
            "account_id": app.config["TEST_ACCOUNT_ID"],
            "transaction_type": "deposit",
            "amount": 100.00,
            "description": "Test deposit",
            "metadata": {"source": "pytest"},
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["transaction_type"] == "deposit"
    assert data["data"]["amount"] == 100.0

    with app.app_context():
        account = db.session.get(Account, app.config["TEST_ACCOUNT_ID"])
        assert float(account.balance) == 1100.0


def test_get_budgets_allows_admin_access(admin_client):
    """Budget listing should be available to admin users."""
    response = admin_client.get("/api/v1/budgets")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["count"] == 0


def test_dashboard_stats_summarize_current_user_data(user_client):
    """Dashboard stats should summarize the authenticated user's accounts."""
    response = user_client.get("/api/v1/dashboard/stats")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["account_count"] == 1
    assert data["data"]["total_balance"] == 1000.0
