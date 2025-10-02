"""
GOFAP - Government Operations and Financial Accounting Platform
Main application entry point with comprehensive Flask setup.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import json

# Import configuration settings
try:
    from configs.settings import *
except ImportError:
    # Fallback if configs module is not available
    DEBUG = True
    SECRET_KEY = 'dev-key-change-in-production'
    DATABASE_URI = 'sqlite:///gofap.db'

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('gofap.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import models after db initialization
from models import db, User, Account, Transaction, Budget, BudgetItem, AuditLog, UserRole, AccountType, TransactionType, TransactionStatus

# Import blueprints
from auth import auth_bp
from api import api_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Main routes
@app.route('/')
def home():
    """Home page route for GOFAP."""
    if current_user.is_authenticated:
        return render_template('dashboard.html', user=current_user)
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with financial overview."""
    # Get user's accounts
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Calculate total balance
    total_balance = sum(float(account.balance) for account in accounts)
    
    return render_template('dashboard.html', 
                         user=current_user,
                         accounts=accounts,
                         recent_transactions=recent_transactions,
                         total_balance=total_balance)

@app.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    """API endpoint to get user's accounts."""
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    return jsonify([account.to_dict() for account in accounts])

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """API endpoint to get user's transactions."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'transactions': [transaction.to_dict() for transaction in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': page
    })

@app.route('/api/budgets', methods=['GET'])
@login_required
def get_budgets():
    """API endpoint to get budgets."""
    if current_user.role in [UserRole.ADMIN, UserRole.TREASURER, UserRole.ACCOUNTANT]:
        budgets = Budget.query.filter_by(is_active=True).all()
    else:
        budgets = Budget.query.filter_by(department=current_user.department, is_active=True).all()
    
    return jsonify([budget.to_dict() for budget in budgets])

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': VERSION
    })

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables."""
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@gofap.gov',
            first_name='System',
            last_name='Administrator',
            role=UserRole.ADMIN,
            department='IT'
        )
        admin_user.set_password('admin123')  # Change in production!
        db.session.add(admin_user)
        db.session.commit()
        logger.info("Created default admin user")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=DEBUG)
