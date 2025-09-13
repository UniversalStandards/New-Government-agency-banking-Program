# GOFAP Development Guide

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Quick Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd New-Government-agency-banking-Program
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Configure environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   python main.py
   ```

5. Visit http://localhost:5000

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
export FLASK_APP=main.py
flask db init
flask db migrate
flask db upgrade

# Run the application
python main.py
```

## Project Structure

```
GOFAP/
├── main.py                 # Flask application entry point
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── Procfile               # Heroku deployment config
├── runtime.txt            # Python version for Heroku
├── .env.template          # Environment variables template
│
├── api/                   # API blueprints
│   ├── accounts.py        # Account management endpoints
│   └── transactions.py    # Transaction endpoints
│
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── account.py
│   └── transaction.py
│
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── dashboard.html     # Dashboard
│   ├── 404.html           # Error pages
│   └── 500.html
│
├── static/                # Static assets
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── main.js
│
├── configs/               # Configuration files
│   └── settings.py
│
├── modern_treasury/       # Modern Treasury integration
│   ├── main.py
│   └── modern_treasury_helpers.py
│
├── stripe/                # Stripe integration
│   ├── main.py
│   └── stripe_helpers.py
│
└── gui/                   # GUI components
    ├── gui_main.py
    └── gui_helpers.py
```

## API Documentation

### Authentication
Currently, the API does not require authentication. In production, implement proper authentication and authorization.

### Endpoints

#### Health Check
- **GET** `/api/health`
- Returns system health status

#### System Information
- **GET** `/api/system/info`
- Returns detailed system information

#### Accounts
- **GET** `/api/accounts` - List accounts
- **POST** `/api/accounts` - Create account
- **GET** `/api/accounts/{id}` - Get account details
- **PUT** `/api/accounts/{id}` - Update account
- **GET** `/api/accounts/{id}/balance` - Get account balance

#### Transactions
- **GET** `/api/transactions` - List transactions
- **POST** `/api/transactions` - Create transaction
- **GET** `/api/transactions/{id}` - Get transaction details
- **PUT** `/api/transactions/{id}/status` - Update transaction status
- **GET** `/api/transactions/summary` - Get transaction summary

#### Integrations
- **GET** `/api/integrations` - List available integrations

## Configuration

### Environment Variables

Create a `.env` file based on `.env.template`:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///gofap.db

# API Keys
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
MODERN_TREASURY_API_KEY=your_mt_key

# Application Settings
APP_NAME=GOFAP
LOG_LEVEL=INFO
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_accounts.py

# Run with coverage
pytest --cov=.
```

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

## Deployment

### Heroku Deployment

1. Create Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set STRIPE_SECRET_KEY=your-stripe-key
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

### Docker Deployment

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "main:app"]
```

## Integrations

### Stripe Integration

The Stripe integration handles:
- Customer creation
- Payment processing  
- Card management

Configure with your Stripe API keys in `.env`.

### Modern Treasury Integration

The Modern Treasury integration handles:
- Account management
- Payment orders
- Treasury operations

Configure with your Modern Treasury API key in `.env`.

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Database**: Use environment variables for database URLs
3. **HTTPS**: Always use HTTPS in production
4. **Authentication**: Implement proper user authentication
5. **Authorization**: Add role-based access control
6. **Input Validation**: Validate all user inputs
7. **SQL Injection**: Use SQLAlchemy ORM properly
8. **XSS Protection**: Escape user-generated content

## Monitoring and Logging

- Configure logging levels via `LOG_LEVEL` environment variable
- Monitor application health via `/api/health` endpoint
- Set up error tracking with Sentry or similar service
- Monitor database performance
- Track API usage and response times

## Government Compliance

GOFAP is designed for government use and should comply with:

- **FISMA** - Federal Information Security Management Act
- **FedRAMP** - Federal Risk and Authorization Management Program  
- **Section 508** - Accessibility requirements
- **FOIA** - Freedom of Information Act
- **Privacy Act** - Personal information protection

## Support

For technical support:

- **Phone**: (844) 697-7877 ext 6327
- **Email**: gofap@ofaps.spurs.gov
- **Organization**: Office of Finance, Accounting, and Procurement Services (OFAPS)

*"We Account for Everything"*

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

This project is developed for government use and follows applicable government licensing requirements.