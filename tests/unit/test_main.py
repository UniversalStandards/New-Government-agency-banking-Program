"""Unit tests for the main application module."""

import pytest
from main import app


def test_app_creation():
    """Test that the Flask app is created properly."""
    assert app is not None
    # In test mode, the database URI will be different (temporary file)
    # So we just check that it's set to some SQLite database
    assert "sqlite:///" in app.config["SQLALCHEMY_DATABASE_URI"]


def test_home_route(client):
    """Test the home route returns expected response."""
    response = client.get("/")
    assert response.status_code == 200
    # Check for HTML content and GOFAP text
    response_text = response.get_data(as_text=True)
    assert "GOFAP" in response_text
    assert "Government Operations and Financial Accounting Platform" in response_text


def test_app_debug_setting(app_context):
    """Test that debug setting is properly configured."""
    # In test mode, debug should be either True or False (not None)
    assert isinstance(app.config.get("DEBUG"), bool)
