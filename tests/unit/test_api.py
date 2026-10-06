"""Unit tests for current API endpoints."""

import json


def test_health_endpoint(client):
    """Test the versioned API health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_accounts_endpoint_requires_login(client):
    """Protected account endpoints should require authentication."""
    response = client.get("/api/v1/accounts")
    assert response.status_code == 302


def test_transactions_endpoint_requires_login(client):
    """Protected transaction endpoints should require authentication."""
    response = client.get("/api/v1/transactions")
    assert response.status_code == 302


def test_404_error_handling(client):
    """Unknown versioned API endpoints should return not found."""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
