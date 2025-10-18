"""
GOFAP - Government Operations and Financial Accounting Platform
Main application entry point with comprehensive Flask setup.
"""

import logging
import os
from datetime import datetime

from flask import Flask, flash, jsonify, render_template, request
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate

from models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import configuration settings
try:
    pass
except ImportError:
    # Fallback if configs module is not available
    DEBUG = True
    SECRET_KEY = "dev-key-change-in-production"
    DATABASE_URI = "sqlite:///gofap.db"

# Initialize Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.FileHandler("gofap.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

from api import api_bp

# Import blueprints
from auth import auth_bp

# Import models after db initialization
from models import Account, Budget, Transaction, User, UserRole, db

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Import models after db initialization
try:
    from models import Account, Budget, Department, Transaction, User  # noqa: F401
except ImportError:
    # Models module not yet created - this is expected during initial setup
    try:
        pass
    except ImportError:
        pass

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User

    return User.query.get(user_id)

# Template context processor
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# Add cache control headers for static files in development
@app.after_request
def add_header(response):
    """Add headers to prevent caching of static files during development."""
    if DEBUG and request.path.startswith("/static/"):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Register blueprints
try:
    from routes import data_import_bp

    app.register_blueprint(data_import_bp)
    logging.info("Data import routes registered")
except ImportError as e:
    logging.warning(f"Could not register data import routes: {e}")

# Register payment routes
try:
    from routes.payments import payments_bp

    app.register_blueprint(payments_bp)
    logging.info("Payment routes registered")
except ImportError as e:
    logging.warning(f"Could not register payment routes: {e}")

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
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500

# Main routes
@app.route("/")
def home():
    """Home page route for GOFAP."""
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user)
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "GOFAP"}

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page showing system overview."""
    try:
        from models import Account, Budget, Transaction

        # Get user's accounts
        user_accounts = Account.query.filter_by(user_id=current_user.id).all()
        total_balance = sum(acc.balance for acc in user_accounts)

        # Get recent transactions
        recent_transactions = (
            Transaction.query.join(Account)
            .filter(Account.user_id == current_user.id)
            .order_by(Transaction.created_at.desc())
            .limit(10)
            .all()
        )

        # Get budget information
        user_budgets = (
            Budget.query.join(Department)
            .join(Account)
            .filter(Account.user_id == current_user.id)
            .all()
        )

        return render_template(
            "dashboard.html",
            accounts=user_accounts,
            total_balance=total_balance,
            recent_transactions=recent_transactions,
            budgets=user_budgets,
        )
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        flash("Error loading dashboard data", "error")
        return render_template("dashboard.html")

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

@app.route("/api/accounts", methods=["GET"])
@login_required
def get_accounts():
    """API endpoint to get user's accounts."""
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    return jsonify([account.to_dict() for account in accounts])

@app.route("/payments")
@login_required
def payments():
    """Payment processing page."""
    try:
        return render_template("payments.html")
    except:
        return jsonify({"message": "GOFAP Payment Processing"})

@app.route("/api/budgets", methods=["GET"])
@login_required
def get_budgets():
    """API endpoint to get budgets."""
    if current_user.role in [UserRole.ADMIN, UserRole.TREASURER, UserRole.ACCOUNTANT]:
        budgets = Budget.query.filter_by(is_active=True).all()
    else:
        budgets = Budget.query.filter_by(
            department=current_user.department, is_active=True
        ).all()

    return jsonify([budget.to_dict() for budget in budgets])

if __name__ == "__main__":
    # Create tables and initialize database
    with app.app_context():
        db.create_all()

        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@gofap.gov",
                first_name="System",
                last_name="Administrator",
                role=UserRole.ADMIN,
                department="IT",
            )
            admin_user.set_password("admin123")  # Change in production!
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Created default admin user")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=DEBUG)
