"""Integration tests for the full application."""

from main import app, db

def test_app_integration_with_database(client):
    """Test that the app integrates properly with the database."""
    # Test that the application can handle database operations
    with app.app_context():
        # This tests that the database connection works
        try:
            db.create_all()
            db.drop_all()
            integration_success = True
        except Exception:
            integration_success = False

    assert integration_success

def test_full_application_startup(client):
    """Test that the full application starts up correctly."""
    # Test basic functionality end-to-end
    response = client.get("/")
    assert response.status_code == 200
    assert "GOFAP" in response.get_data(as_text=True)

def test_error_handling(client):
    """Test that the application handles errors gracefully."""
    # Test a non-existent route
    response = client.get("/nonexistent-route")
    assert response.status_code == 404
