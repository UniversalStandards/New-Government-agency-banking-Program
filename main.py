import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gofap.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional flask-migrate support
try:
    from flask_migrate import Migrate
    migrate = Migrate(app, db)
    logger.info("Flask-Migrate enabled")
except ImportError:
    logger.warning("Flask-Migrate not installed - database migrations not available")
    migrate = None

# Import and register API blueprints
try:
    from api.accounts import accounts_bp
    from api.transactions import transactions_bp
    
    app.register_blueprint(accounts_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    logger.info("API blueprints registered successfully")
except ImportError as e:
    logger.warning(f"Could not import API blueprints: {e}")

# Define models here to avoid circular imports
from datetime import datetime

class User(db.Model):
    """User model for government employees and citizens"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True)
    department = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Account(db.Model):
    """Bank account model"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    routing_number = db.Column(db.String(9))
    bank_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    modern_treasury_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Account {self.account_number}>'

class Transaction(db.Model):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    stripe_payment_intent_id = db.Column(db.String(100))
    modern_treasury_payment_id = db.Column(db.String(100))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'

@app.route('/')
def home():
    """Main landing page for GOFAP"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = 'unhealthy'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'service': 'GOFAP',
        'version': '1.0.0',
        'database': db_status,
        'components': {
            'web_server': 'healthy',
            'database': db_status,
            'stripe_integration': 'ready',
            'modern_treasury_integration': 'ready'
        }
    })

@app.route('/dashboard')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    """Admin panel"""
    return jsonify({
        'message': 'Admin panel - to be implemented',
        'features': [
            'User management',
            'System configuration',
            'Audit logs',
            'Report generation'
        ]
    })

@app.route('/api/system/info')
def system_info():
    """System information endpoint"""
    return jsonify({
        'name': 'GOFAP',
        'full_name': 'Government Operations and Financial Accounting Platform',
        'version': '1.0.0',
        'description': 'Comprehensive finance management platform for government entities',
        'features': [
            'Digital Account & Card Creation',
            'Revenue & Spend Management', 
            'Payment Operations',
            'Treasury Tools',
            'HR Management',
            'Constituent Services',
            'Procurement & Expenses'
        ],
        'contact': {
            'organization': 'Office of Finance, Accounting, and Procurement Services (OFAPS)',
            'phone': '(844) 697-7877 ext 6327',
            'email': 'gofap@ofaps.spurs.gov',
            'motto': 'We Account for Everything'
        }
    })

@app.route('/api/integrations')
def list_integrations():
    """List available integrations"""
    return jsonify({
        'integrations': {
            'stripe': {
                'name': 'Stripe',
                'description': 'Payment processing and card creation',
                'status': 'configured' if os.environ.get('STRIPE_SECRET_KEY') else 'not_configured',
                'features': ['payment_processing', 'customer_management', 'card_issuance']
            },
            'modern_treasury': {
                'name': 'Modern Treasury',
                'description': 'Treasury management and banking operations',
                'status': 'configured' if os.environ.get('MODERN_TREASURY_API_KEY') else 'not_configured',
                'features': ['account_management', 'payment_orders', 'cash_flow_management']
            }
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': f'The requested endpoint {request.path} was not found'
        }), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    return render_template('500.html'), 500

# CLI commands for development
@app.cli.command()
def init_db():
    """Initialize the database"""
    try:
        db.create_all()
        logger.info("Database initialized successfully")
        print("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        print(f"Error initializing database: {e}")

@app.cli.command()
def create_sample_data():
    """Create sample data for testing"""
    try:
        # TODO: Implement sample data creation when models are ready
        logger.info("Sample data creation - to be implemented")
        print("Sample data creation - to be implemented")
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        print(f"Error creating sample data: {e}")

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])



