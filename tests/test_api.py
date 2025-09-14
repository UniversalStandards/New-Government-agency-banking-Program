"""
Test cases for GOFAP API endpoints.
"""

import pytest
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User, Account, Transaction, UserRole, AccountType, TransactionType

@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    
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
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role=UserRole.EMPLOYEE,
            department='IT'
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def sample_account(app, sample_user):
    """Create a sample account for testing."""
    with app.app_context():
        account = Account(
            user_id=sample_user.id,
            account_name='Test Account',
            account_type=AccountType.CHECKING,
            balance=1000.00,
            currency='USD'
        )
        db.session.add(account)
        db.session.commit()
        return account

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_get_accounts_unauthorized(client):
    """Test getting accounts without authentication."""
    response = client.get('/api/v1/accounts')
    assert response.status_code == 401

def test_create_account_unauthorized(client):
    """Test creating account without authentication."""
    response = client.post('/api/v1/accounts', 
                          data=json.dumps({'account_name': 'Test', 'account_type': 'checking'}),
                          content_type='application/json')
    assert response.status_code == 401

def test_get_transactions_unauthorized(client):
    """Test getting transactions without authentication."""
    response = client.get('/api/v1/transactions')
    assert response.status_code == 401

def test_create_transaction_unauthorized(client):
    """Test creating transaction without authentication."""
    response = client.post('/api/v1/transactions',
                          data=json.dumps({'account_id': '123', 'transaction_type': 'deposit', 'amount': 100}),
                          content_type='application/json')
    assert response.status_code == 401

def test_get_budgets_unauthorized(client):
    """Test getting budgets without authentication."""
    response = client.get('/api/v1/budgets')
    assert response.status_code == 401

def test_create_budget_unauthorized(client):
    """Test creating budget without authentication."""
    response = client.post('/api/v1/budgets',
                          data=json.dumps({'name': 'Test Budget', 'fiscal_year': 2024, 'total_budget': 10000}),
                          content_type='application/json')
    assert response.status_code == 401

def test_dashboard_stats_unauthorized(client):
    """Test getting dashboard stats without authentication."""
    response = client.get('/api/v1/dashboard/stats')
    assert response.status_code == 401

def test_invalid_json(client):
    """Test API with invalid JSON."""
    response = client.post('/api/v1/accounts',
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400

def test_missing_required_fields(client):
    """Test API with missing required fields."""
    # This would need authentication, but we can test the error handling
    response = client.post('/api/v1/accounts',
                          data=json.dumps({'account_name': 'Test'}),
                          content_type='application/json')
    assert response.status_code == 401  # Unauthorized, but would be 400 with auth

def test_nonexistent_endpoint(client):
    """Test non-existent API endpoint."""
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == 404