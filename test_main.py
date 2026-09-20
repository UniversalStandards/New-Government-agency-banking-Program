"""Basic tests for GOFAP application."""

import pytest

from main import app, db
from models import User, UserRole


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated admin client for protected routes."""
    with app.app_context():
        user = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )
        user.set_password("Admin1234")
        db.session.add(user)
        db.session.commit()

        user_id = user.id

    with client.session_transaction() as session:
        session["_user_id"] = user_id
        session["_fresh"] = True

    return client


def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to GOFAP" in response.data


def test_dashboard_page(authenticated_client):
    """Test that the dashboard page loads successfully."""
    response = authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_accounts_page(authenticated_client):
    """Test that the accounts page loads successfully."""
    response = authenticated_client.get("/accounts")
    assert response.status_code == 200
    assert b"Account Management" in response.data


def test_create_account_page(authenticated_client):
    """Test that the create account page loads successfully."""
    response = authenticated_client.get("/accounts/create")
    assert response.status_code == 200
    assert b"Create New Account" in response.data


def test_api_create_account_missing_fields(authenticated_client):
    """Test API account creation with missing fields."""
    response = authenticated_client.post(
        "/api/accounts/create", json={}, content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_create_account_valid(authenticated_client):
    """Test API account creation with valid data."""
    response = authenticated_client.post(
        "/api/accounts/create",
        json={
            "service": "stripe",
            "account_type": "checking",
            "account_name": "Test Account",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "account_id" in data


def test_api_create_account_invalid_service(authenticated_client):
    """Test API account creation rejects unsupported services."""
    response = authenticated_client.post(
        "/api/accounts/create",
        json={
            "service": "invalid",
            "account_type": "checking",
            "account_name": "Test Account",
        },
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "Invalid service" in response.get_json()["error"]


def test_transactions_page(client):
    """Test that the transactions page loads successfully."""
    response = client.get("/transactions")
    assert response.status_code == 200
    assert b"Transactions" in response.data


def test_budgets_page(client):
    """Test that the budgets page loads successfully."""
    response = client.get("/budgets")
    assert response.status_code == 200
    assert b"Budget Management" in response.data


def test_reports_page(client):
    """Test that the reports page loads successfully."""
    response = client.get("/reports")
    assert response.status_code == 200
    assert b"Reports" in response.data
