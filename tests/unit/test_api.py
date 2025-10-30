"""Unit tests for API endpoints."""

import pytest
import json
from main import app, db
from models import (
    User,
    Account,
    Transaction,
    UserRole,
    TransactionType,
    TransactionStatus,
)


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_users_get_endpoint(client):
    """Test the users GET endpoint."""
    response = client.get("/api/users")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_users_post_endpoint(client):
    """Test creating a user via POST."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "employee",
    }

    response = client.post(
        "/api/users", data=json.dumps(user_data), content_type="application/json"
    )
    assert response.status_code == 201

    data = json.loads(response.data)
    assert data["message"] == "User created successfully"
    assert "user_id" in data


def test_accounts_get_endpoint(client):
    """Test the accounts GET endpoint."""
    response = client.get("/api/accounts")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_transactions_get_endpoint(client):
    """Test the transactions GET endpoint."""
    response = client.get("/api/transactions")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_budget_endpoint(client):
    """Test the budget information endpoint."""
    response = client.get("/api/budget")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_payroll_get_endpoint(client):
    """Test the payroll GET endpoint."""
    response = client.get("/api/payroll")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_utilities_get_endpoint(client):
    """Test the utilities GET endpoint."""
    response = client.get("/api/utilities")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)


def test_404_error_handling(client):
    """Test that 404 errors are handled properly."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

    data = json.loads(response.data)
    assert data["error"] == "Not found"
