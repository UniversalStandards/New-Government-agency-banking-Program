"""
GOFAP - Government Operations and Financial Accounting Platform
Main application entry point with comprehensive Flask setup.
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import configuration settings
try:
    from configs.settings import DATABASE_URI, DEBUG, SECRET_KEY
except ImportError:
    # Fallback if configs module is not available
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_URI = 'sqlite:///gofap.db'

# Initialize Flask application
app = Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warning
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
    DATABASE_URI = "sqlite:///gofap.db"

# Initialize Flask application
app = Flask(__name__)
app.config["DEBUG"] = DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.FileHandler("gofap.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

from api import api_bp

# Import blueprints
from auth import auth_bp

# Import models after db initialization
from models import User, UserRole

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
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
except ImportError:
    pass  # Data import routes not available

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return jsonify({'error': 'Internal server error'}), 500

# Register data import routes
try:
    from routes import data_import_bp
    app.register_blueprint(data_import_bp)
    logging.info("Data import routes registered")
except ImportError as e:
    logging.warning(f"Could not register data import routes: {e}")
    return jsonify({"error": "Internal server error"}), 500

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

# Main application routes
@app.route("/")
def home():
    """Home page route."""
    if current_user.is_authenticated:
        try:
            return render_template("dashboard.html", user=current_user)
        except:
            return render_template("index.html")
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint (non-API)."""
    return jsonify({"status": "healthy", "service": "GOFAP"})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


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
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500

# Main routes - minimal routes, most are in blueprints

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
