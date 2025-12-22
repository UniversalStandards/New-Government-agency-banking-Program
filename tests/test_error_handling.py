"""
Tests for secure error handling to prevent information exposure.
"""

from unittest.mock import patch

import pytest
from flask import Flask

from utils import safe_error_response

def test_safe_error_response_logs_full_exception():
    """Test that safe_error_response logs the full exception details."""
    test_exception = ValueError("Database connection failed: localhost:5432")

    with patch("utils.logger") as mock_logger:
        result = safe_error_response(test_exception, "Database error occurred")

        # Verify the full exception was logged
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "ValueError" in log_message
        assert "Database connection failed" in log_message

        # Verify generic message was returned
        assert result == "Database error occurred"

def test_safe_error_response_returns_default_message():
    """Test that safe_error_response returns the default generic message."""
    test_exception = Exception("Internal server error with sensitive data")

    result = safe_error_response(test_exception)

    # Should return default message, not the sensitive exception message
    assert result == "An error occurred"
    assert "sensitive data" not in result

def test_safe_error_response_with_custom_message():
    """Test that safe_error_response returns custom message."""
    test_exception = RuntimeError("File not found: /etc/secrets/config.yml")
    custom_message = "Failed to load configuration"

    result = safe_error_response(test_exception, custom_message)

    # Should return custom message, not file path
    assert result == custom_message
    assert "/etc/secrets" not in result
    assert "config.yml" not in result

def test_safe_error_response_prevents_stacktrace_exposure():
    """Test that safe_error_response doesn't expose stack traces."""
    test_exception = Exception("Traceback (most recent call last)...")

    result = safe_error_response(test_exception, "Operation failed")

    # Should not contain stack trace information
    assert "Traceback" not in result
    assert result == "Operation failed"

def test_safe_error_response_handles_different_exception_types():
    """Test that safe_error_response handles various exception types."""
    exceptions = [
        (ValueError("Invalid value"), "Validation error"),
        (KeyError("secret_key"), "Key not found"),
        (RuntimeError("Runtime error"), "Runtime error occurred"),
        (TypeError("Type mismatch"), "Type error"),
    ]

    for exception, message in exceptions:
        result = safe_error_response(exception, message)
        assert result == message
        # Ensure no exception details are in the result
        assert str(exception) not in result

@pytest.fixture
def app():
    """Create a test Flask app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_route_error_handling_with_database_error(app, client):
    """Test that routes handle database errors securely."""
    from flask import jsonify

    @app.route("/test-db-error")
    def test_endpoint():
        try:
            # Simulate a database error
            raise Exception(
                "FATAL: password authentication failed for user 'admin' at host '192.168.1.100'"
            )
        except Exception as e:
            error_msg = safe_error_response(e, "Database operation failed")
            return jsonify({"error": error_msg}), 500

    response = client.get("/test-db-error")
    data = response.get_json()

    assert response.status_code == 500
    assert data["error"] == "Database operation failed"
    # Ensure no sensitive information is leaked
    assert "password" not in data["error"].lower()
    assert "192.168.1.100" not in data["error"]
    assert "admin" not in data["error"]

def test_route_error_handling_with_api_error(app, client):
    """Test that routes handle API errors securely."""
    from flask import jsonify

    @app.route("/test-api-error")
    def test_endpoint():
        try:
            # Simulate an API error with credentials
            raise Exception(
                "API request failed: Invalid API key 'sk_test_abc123xyz' for account 'acct_xyz789'"
            )
        except Exception as e:
            error_msg = safe_error_response(e, "API request failed")
            return jsonify({"error": error_msg}), 500

    response = client.get("/test-api-error")
    data = response.get_json()

    assert response.status_code == 500
    assert data["error"] == "API request failed"
    # Ensure API keys and account IDs are not leaked
    assert "sk_test_" not in data["error"]
    assert "acct_" not in data["error"]

def test_route_error_handling_with_file_path_error(app, client):
    """Test that routes handle file path errors securely."""
    from flask import jsonify

    @app.route("/test-path-error")
    def test_endpoint():
        try:
            # Simulate a file error with system paths
            raise Exception(
                "FileNotFoundError: [Errno 2] No such file or directory: '/home/admin/.ssh/id_rsa'"
            )
        except Exception as e:
            error_msg = safe_error_response(e, "File operation failed")
            return jsonify({"error": error_msg}), 500

    response = client.get("/test-path-error")
    data = response.get_json()

    assert response.status_code == 500
    assert data["error"] == "File operation failed"
    # Ensure file paths are not leaked
    assert "/home/" not in data["error"]
    assert ".ssh" not in data["error"]
    assert "id_rsa" not in data["error"]

def test_service_error_handling():
    """Test that service methods use safe error handling."""

    # This tests the pattern used in services
    def mock_service_method():
        try:
            # Simulate service error
            raise Exception(
                "Connection refused: Unable to connect to database at postgresql://user:pass@localhost:5432/gofap"
            )
        except Exception as e:
            error_msg = safe_error_response(e, "Service unavailable")
            return {"success": False, "error": error_msg}

    result = mock_service_method()

    assert result["success"] is False
    assert result["error"] == "Service unavailable"
    # Ensure database credentials are not leaked
    assert "postgresql://" not in result["error"]
    assert "user:pass" not in result["error"]
    assert "localhost:5432" not in result["error"]
