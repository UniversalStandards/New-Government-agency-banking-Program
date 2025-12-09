"""
GOFAP - Government Operations and Financial Accounting Platform
Main application entry point with comprehensive Flask setup.
"""

import logging
import os
import uuid
from datetime import datetime  # Removed timedelta since it's not used
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
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
    from configs.settings import DEBUG, SECRET_KEY, DATABASE_URI
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
db = SQLAlchemy(app)
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
    from models import User, Account, Transaction, PayrollRecord, Budget, UtilityPayment
    from models import UserRole, TransactionType, TransactionStatus
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

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    """Home page route for the GOFAP Payment Processor."""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GOFAP - Government Operations and Financial Accounting Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #1E90FF; }
            .features { margin: 20px 0; }
            .feature { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
            .api-link { color: #FF4500; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1 class="header">Welcome to GOFAP</h1>
        <h2>Government Operations and Financial Accounting Platform</h2>
        
        <div class="features">
            <h3>Available Features:</h3>
            <div class="feature">💳 Digital Account & Card Management</div>
            <div class="feature">💰 Payment Processing & Treasury Management</div>
            <div class="feature">👥 HR & Payroll Management</div>
            <div class="feature">👤 Constituent Services</div>
            <div class="feature">📊 Budgeting & Financial Analytics</div>
        </div>
        
        <div class="api-endpoints">
            <h3>API Endpoints:</h3>
            <ul>
                <li><a href="/api/health" class="api-link">GET /api/health</a> - System health check</li>
                <li><a href="/api/users" class="api-link">GET /api/users</a> - List all users</li>
                <li><a href="/api/accounts" class="api-link">GET /api/accounts</a> - List all accounts</li>
                <li><a href="/api/transactions" class="api-link">GET /api/transactions</a> - List transactions</li>
                <li><a href="/api/budget" class="api-link">GET /api/budget</a> - Budget information</li>
            </ul>
        </div>
        
        <p><strong>Version:</strong> 1.0.0</p>
    </body>
    </html>
    """)


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """User management endpoint."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=UserRole(data.get('role', 'citizen'))
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'User created successfully', 'user_id': user.id}), 201
        
        else:
            users_list = User.query.all()
            return jsonify([{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}",
                'role': user.role.value,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            } for user in users_list])
    
    except Exception as e:
        # Log the exception internally for debugging
        logging.exception("Exception in /api/users endpoint")
        return jsonify({'error': 'An internal error has occurred.'}), 500


@app.route('/api/accounts', methods=['GET', 'POST'])
def accounts():
    """Account management endpoint."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            account = Account(
                account_number=str(uuid.uuid4())[:8].upper(),
                account_type=data['account_type'],
                balance=data.get('initial_balance', 0.0),
                user_id=data['user_id']
            )
            db.session.add(account)
            db.session.commit()
            return jsonify({'message': 'Account created successfully', 'account_id': account.id}), 201
        
        else:
            accounts_list = Account.query.all()
            return jsonify([{
                'id': account.id,
                'account_number': account.account_number,
                'account_type': account.account_type,
                'balance': account.balance,
                'user_id': account.user_id,
                'is_active': account.is_active,
                'created_at': account.created_at.isoformat()
            } for account in accounts_list])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['GET', 'POST'])
def transactions():
    """Transaction management endpoint."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=TransactionType(data['transaction_type']),
                amount=data['amount'],
                description=data.get('description', ''),
                user_id=data['user_id'],
                from_account_id=data.get('from_account_id'),
                to_account_id=data.get('to_account_id')
            )
            db.session.add(transaction)
            db.session.commit()
            return jsonify({'message': 'Transaction created successfully', 'transaction_id': transaction.id}), 201
        
        else:
            transactions_list = Transaction.query.order_by(Transaction.created_at.desc()).limit(100).all()
            return jsonify([{
                'id': transaction.id,
                'transaction_id': transaction.transaction_id,
                'type': transaction.transaction_type.value,
                'status': transaction.status.value,
                'amount': transaction.amount,
                'currency': transaction.currency,
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat()
            } for transaction in transactions_list])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/budget')
def budget_info():
    """Budget information endpoint."""
    try:
        budgets = Budget.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': budget.id,
            'name': budget.name,
            'department': budget.department,
            'fiscal_year': budget.fiscal_year,
            'allocated_amount': budget.allocated_amount,
            'spent_amount': budget.spent_amount,
            'remaining_amount': budget.allocated_amount - budget.spent_amount,
            'utilization_percentage': round((budget.spent_amount / budget.allocated_amount) * 100, 2) if budget.allocated_amount > 0 else 0
        } for budget in budgets])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payroll', methods=['GET', 'POST'])
def payroll():
    """Payroll management endpoint."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            payroll_record = PayrollRecord(
                employee_id=data['employee_id'],
                pay_period_start=datetime.fromisoformat(data['pay_period_start']),
                pay_period_end=datetime.fromisoformat(data['pay_period_end']),
                gross_pay=data['gross_pay'],
                net_pay=data['net_pay'],
                tax_withheld=data.get('tax_withheld', 0.0),
                benefits_deduction=data.get('benefits_deduction', 0.0),
                other_deductions=data.get('other_deductions', 0.0)
            )
            db.session.add(payroll_record)
            db.session.commit()
            return jsonify({'message': 'Payroll record created successfully'}), 201
        
        else:
            payroll_records = PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).limit(50).all()
            return jsonify([{
                'id': record.id,
                'employee_id': record.employee_id,
                'pay_period_start': record.pay_period_start.isoformat(),
                'pay_period_end': record.pay_period_end.isoformat(),
                'gross_pay': record.gross_pay,
                'net_pay': record.net_pay,
                'processed': record.processed
            } for record in payroll_records])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/utilities', methods=['GET', 'POST'])
def utilities():
    """Utility payment management endpoint."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            utility_payment = UtilityPayment(
                citizen_id=data['citizen_id'],
                utility_type=data['utility_type'],
                account_number=data['account_number'],
                amount_due=data['amount_due'],
                due_date=datetime.fromisoformat(data['due_date'])
            )
            db.session.add(utility_payment)
            db.session.commit()
            return jsonify({'message': 'Utility payment record created successfully'}), 201
        
        else:
            utility_payments = UtilityPayment.query.order_by(UtilityPayment.due_date.desc()).limit(50).all()
            return jsonify([{
                'id': payment.id,
                'citizen_id': payment.citizen_id,
                'utility_type': payment.utility_type,
                'account_number': payment.account_number,
                'amount_due': payment.amount_due,
                'amount_paid': payment.amount_paid,
                'due_date': payment.due_date.isoformat(),
                'is_paid': payment.is_paid
            } for payment in utility_payments])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return jsonify({'error': 'Internal server error'}), 500
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=DEBUG)
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
