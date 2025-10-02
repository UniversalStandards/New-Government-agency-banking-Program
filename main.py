"""
GOFAP - Government Operations and Financial Accounting Platform
Main application entry point with comprehensive Flask setup.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import json

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    from configs.settings import DEBUG, SECRET_KEY, DATABASE_URI
except ImportError:
    # Fallback if configs module is not available
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes", "on")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
    DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///gofap.db")

# Initialize Flask application
app = Flask(__name__)
app.config["DEBUG"] = DEBUG
app.config["SECRET_KEY"] = SECRET_KEY

# Initialize the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
# Import models after db initialization
try:
    from models import User, Account, Transaction, Department, Budget
except ImportError:
    # Models module not yet created - this is expected during initial setup
    try:
        from models import *
    except ImportError:
        pass

# Register blueprints
try:
    from routes import data_import_bp
    app.register_blueprint(data_import_bp)
    logging.info("Data import routes registered")
except ImportError as e:
    logging.warning(f"Could not register data import routes: {e}")

# Register CLI commands
try:
    from cli import register_data_import_commands
    register_data_import_commands(app)
    logging.info("Data import CLI commands registered")
except ImportError as e:
    logging.warning(f"Could not register data import CLI commands: {e}")

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
@app.route("/")
def home():
    """Home page route for the GOFAP Payment Processor."""
    try:
        return render_template("index.html")
    except:
        return "Welcome to the Government Operations and Financial Accounting Platform (GOFAP)!"


@app.route("/dashboard")
def dashboard():
    """Dashboard page showing system overview."""
    try:
        return render_template("dashboard.html")
    except:
        return jsonify({"message": "GOFAP Dashboard - System Overview"})


@app.route("/accounts")
def accounts():
    """Accounts management page."""
    try:
        return render_template("accounts.html")
    except:
        return jsonify({"message": "GOFAP Account Management"})


@app.route("/accounts/create")
def create_account():
    """Account creation page."""
    try:
        return render_template("create_account.html")
    except:
        return jsonify({"message": "GOFAP Account Creation"})


@app.route("/api/accounts/create", methods=["POST"])
def api_create_account():
    """API endpoint for creating accounts."""
    try:
        data = request.get_json()
        service = data.get("service")
        account_type = data.get("account_type")
        account_name = data.get("account_name")

        if not all([service, account_type, account_name]):
            return jsonify({"error": "Missing required fields"}), 400

        # Here you would integrate with the actual service APIs
        # For now, return a success response
        return jsonify(
            {
                "success": True,
                "message": f"{service} account created successfully",
                "account_id": f"mock_{service}_{account_type}_account",
            }
        )

    except Exception:
        logging.exception("Exception occurred while creating account")
        return (
            jsonify({"error": "An internal error occurred. Please try again later."}),
            500,
        )


@app.route("/transactions")
def transactions():
    """Transactions page."""
    try:
        return render_template("transactions.html")
    except:
        return jsonify({"message": "GOFAP Transaction Management"})


@app.route("/budgets")
def budgets():
    """Budgets page."""
    try:
        return render_template("budgets.html")
    except:
        return jsonify({"message": "GOFAP Budget Management"})


@app.route("/reports")
def reports():
    """Reports and analytics page."""
    try:
        return render_template("reports.html")
    except:
        return jsonify({"message": "GOFAP Reports and Analytics"})

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
@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'GOFAP'}

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
if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=DEBUG)
