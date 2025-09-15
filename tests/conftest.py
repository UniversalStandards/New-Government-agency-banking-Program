"""Shared test configuration and fixtures for GOFAP tests."""

import pytest
import tempfile
import os
from main import app, db


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app_context():
    """Create an application context for testing."""
    with app.app_context():
        yield app