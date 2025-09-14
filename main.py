import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import configuration settings
try:
    from configs.settings import DEBUG
except ImportError:
    # Fallback if configs module is not available
    DEBUG = True

# Initialize Flask application
app = Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///payment_processor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warning
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import models to ensure they are known to Flask-Migrate
try:
    from models import *
except ImportError:
    # Models module not yet created - this is expected during initial setup
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


@app.route('/')
def home():
    """Home page route for the GOFAP Payment Processor."""
    return '''
    <h1>Welcome to the Government Operations and Financial Accounting Platform (GOFAP)!</h1>
    <p>Your comprehensive finance management platform for government entities.</p>
    <h2>Available Services:</h2>
    <ul>
        <li><a href="/data-import/">Data Import Dashboard</a> - Manage data synchronization with external services</li>
    </ul>
    <h2>Features:</h2>
    <ul>
        <li>💳 Digital Account & Card Creation</li>
        <li>💰 Revenue & Spend Management</li>
        <li>💸 Payment Operations</li>
        <li>📈 Treasury Tools</li>
        <li>🔄 Data Import & Synchronization</li>
    </ul>
    '''


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'GOFAP'}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=DEBUG)
