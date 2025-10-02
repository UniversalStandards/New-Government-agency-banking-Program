# <span style="color: #1E90FF;">Government Operations and Financial Accounting Platform</span> | <span style="color: #FF4500;">GOFAP</span>

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The <span style="color: #FFA500;">**Government Operations and Financial Accounting Platform (GOFAP)**</span> is a comprehensive, production-ready finance management platform built specifically for government entities. This modern web application provides robust capabilities for managing accounting, payments, treasury operations, and more through a beautiful, responsive interface.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for production)
- PostgreSQL (for production)
- Redis (for caching)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gofap
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - Web Interface: http://localhost:5000
   - API Documentation: http://localhost:5000/api/v1/health
   - Default Admin: admin / admin123

### Production Deployment

1. **Deploy with Docker Compose**
   ```bash
   ./deploy.sh
   ```

2. **Or manually with Docker**
   ```bash
   docker-compose up -d
   ```

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask 2.3+ with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **Caching**: Redis
- **Authentication**: Flask-Login with role-based access control
- **API**: RESTful API with comprehensive endpoints
- **Deployment**: Docker containers with Nginx reverse proxy

### Key Features

#### 🔐 **Authentication & Authorization**
- User registration and login
- Role-based access control (Admin, Treasurer, Accountant, HR Manager, etc.)
- Secure password hashing
- Session management

#### 💳 **Account Management**
- Create and manage financial accounts
- Support for multiple account types (Checking, Savings, Credit, Debit)
- Integration with external services (Stripe, Modern Treasury)
- Real-time balance tracking

#### 💰 **Transaction Processing**
- Complete transaction lifecycle management
- Multiple transaction types (Deposit, Withdrawal, Transfer, Payment, Payroll)
- Transaction status tracking
- Comprehensive audit logging

#### 📊 **Budget Management**
- Create and manage budgets by department
- Budget item categorization
- Real-time spending tracking
- Budget vs. actual reporting

#### 🔌 **API Integrations**
- **Stripe**: Payment processing and customer management
- **Modern Treasury**: Advanced treasury operations
- **RESTful API**: Complete API for all operations

#### 📱 **Modern Web Interface**
- Responsive design for all devices
- Intuitive dashboard with key metrics
- Real-time data updates
- Professional government-grade UI

## 📁 Project Structure

```
gofap/
├── main.py                 # Main Flask application
├── models.py              # Database models
├── auth.py                # Authentication routes
├── api.py                 # API endpoints
├── configs/
│   └── settings.py        # Configuration management
├── modern_treasury/
│   ├── main.py           # Modern Treasury integration
│   └── modern_treasury_helpers.py
├── stripe/
│   ├── main.py           # Stripe integration
│   └── stripe_helpers.py
├── gui/
│   ├── gui_main.py       # Legacy GUI (deprecated)
│   └── gui_helpers.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── auth/
│   └── errors/
├── static/              # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Multi-container setup
├── nginx.conf          # Nginx configuration
└── deploy.sh           # Deployment script
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `DEBUG` | Debug mode | True |
| `SECRET_KEY` | Flask secret key | Generated |
| `DATABASE_URL` | Database connection string | sqlite:///gofap.db |
| `STRIPE_SECRET_KEY` | Stripe API secret key | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - |
| `MODERN_TREASURY_API_KEY` | Modern Treasury API key | - |
| `MODERN_TREASURY_ORG_ID` | Modern Treasury organization ID | - |

### Database Models

- **User**: User accounts with role-based permissions
- **Account**: Financial accounts with external service integration
- **Transaction**: Financial transactions with full audit trail
- **Budget**: Department budgets with itemized breakdowns
- **BudgetItem**: Individual budget line items
- **AuditLog**: Comprehensive audit logging

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_models.py
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/register` - User registration

### Account Endpoints
- `GET /api/v1/accounts` - List user accounts
- `POST /api/v1/accounts` - Create new account
- `GET /api/v1/accounts/{id}` - Get account details

### Transaction Endpoints
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction

### Budget Endpoints
- `GET /api/v1/budgets` - List budgets
- `POST /api/v1/budgets` - Create budget

## 🔒 Security Features

- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Rate Limiting**: API rate limiting with Redis
- **Audit Logging**: Complete audit trail
- **Role-Based Access**: Granular permission system

## 🚀 Deployment

### Production Checklist

- [ ] Update `SECRET_KEY` in production
- [ ] Configure external API keys
- [ ] Set up SSL certificates
- [ ] Configure database backups
- [ ] Set up monitoring and logging
- [ ] Configure firewall rules
- [ ] Update default admin password

### Docker Deployment

```bash
# Build and deploy
./deploy.sh

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:

- **Email**: gofap@ofaps.spurs.gov
- **Phone**: (844) 697-7877 ext 6327
- **Documentation**: [API Docs](http://localhost:5000/api/v1/health)

## 🎯 Roadmap

- [ ] Mobile application
- [ ] Advanced reporting and analytics
- [ ] Multi-tenant support
- [ ] Additional payment processors
- [ ] Workflow automation
- [ ] Advanced security features

---

**Office of Finance, Accounting, and Procurement Services (OFAPS)**  
*"We Account for Everything"*