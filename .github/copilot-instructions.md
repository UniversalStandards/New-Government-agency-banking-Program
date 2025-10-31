# Government Operations and Financial Accounting Platform (GOFAP)

GOFAP is a Python Flask-based government financial platform with integrations to Stripe and Modern Treasury APIs. The system provides digital account creation, payment processing, treasury management, HR systems, and constituent services for government agencies.

**ALWAYS follow these instructions first and fallback to additional search and context gathering only if the information in the instructions is incomplete or found to be in error.**

## Technology Stack

- **Backend**: Python 3.12+ with Flask 3.1.2
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Font Awesome 6, vanilla JavaScript
- **APIs**: Stripe, Modern Treasury integrations
- **Testing**: pytest, pytest-flask, pytest-cov
- **Code Quality**: flake8, black, mypy, isort
- **Server**: Flask development server (dev), Gunicorn (production)
- **Frontend Build**: Node.js with Gulp, TypeScript, ESLint
- **CI/CD**: GitHub Actions (17 workflows)

## Quick Start

### Prerequisites
- Python 3.12+ is available at `/usr/bin/python3`
- Node.js and npm for frontend builds
- pip package manager

### Setup Commands (Run in Order)

1. **Install Python dependencies (~20-30 seconds):**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies (if working with frontend):**
   ```bash
   npm install
   ```

3. **Initialize database:**
   ```bash
   python -c "from main import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
   ```
   **Note**: Currently has circular import issue - database setup happens automatically on first `python main.py` run

## Known Issues

### Critical - Circular Import
- **Issue**: `models.py` imports `db` from `main.py` and vice versa
- **Impact**: Direct database initialization via Python shell fails
- **Workaround**: Database is created automatically when running `python main.py`
- **Status**: Pre-existing issue, functional for application startup

### GUI Application
- Located in `gui/gui_main.py`
- Has unresolved import path issues with modern_treasury modules
- Requires DISPLAY environment (not available in headless environments)
- **Do not attempt to run the GUI in CI/CD or headless environments**

## Build and Validation Commands

**CRITICAL: All commands complete quickly (under 5 minutes) - NEVER CANCEL**

### Python Linting and Validation

1. **Critical syntax check (~0.3 seconds):**
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```
   **Must pass** - this checks for syntax errors and undefined names

2. **Full code quality check (~0.2 seconds):**
   ```bash
   flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
   ```

3. **Auto-format code (~0.4 seconds):**
   ```bash
   black .
   ```

4. **Type checking (~0.2 seconds):**
   ```bash
   mypy --ignore-missing-imports --exclude="stripe/main.py" .
   ```
   **Note**: Excludes `stripe/main.py` due to duplicate module name conflict with `modern_treasury/main.py`

5. **Import sorting:**
   ```bash
   isort .
   ```

### Testing

```bash
# Run all tests (~0.3 seconds)
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest test_main.py -v
```

**Note**: Currently minimal test coverage exists

### Frontend Build (if working with static assets)

```bash
# Development build
npm run build:dev

# Production build
npm run build

# Watch mode for development
npm run watch

# Linting
npm run lint

# Type checking
npm run type-check
```

## Running the Application

### Development Server

```bash
python main.py
```
- Runs on http://127.0.0.1:5000
- Auto-reloads on file changes (when DEBUG=True)
- Creates database tables automatically on first run
- Creates default admin user (username: admin, password: admin123)
- **Stop with Ctrl+C**

### Production Server

```bash
gunicorn --bind 127.0.0.1:8000 main:app
```
- Runs on http://127.0.0.1:8000
- Use with production database (PostgreSQL)
- **Stop with Ctrl+C**

### Testing the Application

```bash
# Test home endpoint
curl http://127.0.0.1:5000/

# Expected response
"Welcome to GOFAP - Government Operations and Financial Accounting Platform"
```

## Project Structure

```
/
├── main.py                 # Flask application entry point
├── models.py               # Database models (User, Account, Transaction, etc.)
├── api.py                  # API blueprint
├── auth.py                 # Authentication blueprint
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies and scripts
├── .github/
│   ├── workflows/          # 17 CI/CD workflows
│   ├── copilot-instructions.md  # This file
│   └── WORKFLOWS.md        # Workflow documentation
├── configs/
│   └── settings.py         # Configuration management
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JavaScript, images
├── routes/                 # Additional route blueprints
├── services/               # Business logic services
├── modern_treasury/        # Modern Treasury API integration
│   ├── main.py             # Example usage
│   └── modern_treasury_helpers.py
├── stripe/                 # Stripe API integration
│   ├── main.py             # Example usage
│   └── stripe_helpers.py
├── gui/                    # Tkinter GUI (has import issues)
│   ├── gui_main.py
│   └── gui_helpers.py
├── tests/                  # Test suite
│   ├── test_main.py
│   └── test_smoke.py
├── cli/                    # Command-line interface tools
└── scripts/                # Utility scripts
```

## Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```env
# Flask Configuration
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///gofap.db  # or postgresql://user:pass@localhost/gofap

# API Keys
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
MODERN_TREASURY_API_KEY=your-mt-api-key
MODERN_TREASURY_ORG_ID=your-org-id

# Server
PORT=5000
```

### Settings File

`configs/settings.py` provides configuration defaults:
- DEBUG mode
- SECRET_KEY
- DATABASE_URI

Falls back to environment variables if module import fails.

## Development Workflow

**ALWAYS follow this sequence when making changes:**

1. **Make code changes**

2. **Format code:**
   ```bash
   black .
   isort .
   ```

3. **Check for critical errors:**
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

4. **Run full lint:**
   ```bash
   flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
   ```

5. **Test the application:**
   ```bash
   # Start server
   python main.py &
   
   # Wait 3 seconds for startup
   sleep 3
   
   # Test endpoint
   curl http://127.0.0.1:5000/
   
   # Stop server
   pkill -f "python main.py"
   ```

6. **Run tests:**
   ```bash
   pytest -v
   ```

7. **Commit changes** (only if all checks pass)

## CI/CD Workflows

The repository has **17 GitHub Actions workflows** in `.github/workflows/`:

### Main Workflows
- **ci.yml** - Comprehensive CI with security scanning
- **python-app.yml** - Standard Python CI (Python 3.10)
- **python-package.yml** - Multi-version testing (3.9, 3.10, 3.11)
- **npm-gulp.yml** - Frontend build and testing

### Security Workflows
- **codeql.yml** - CodeQL security analysis
- **dependency-review.yml** - Dependency vulnerability checking
- **security-scan.yml** - Additional security scanning
- **frogbot-scan-pr.yml** - JFrog Xray scanning
- **mobb-codeql.yaml** - Automated vulnerability fixing

### Automation Workflows
- **summary.yml** - AI-powered issue summarization
- **label.yml** & **labeler.yml** - PR auto-labeling
- **auto-fix.yml** - Automated code fixes
- **issue-management.yml** - Issue triage and management
- **documentation.yml** - Documentation generation
- **static.yml** - GitHub Pages deployment
- **python-publish.yml** - PyPI publishing

**See `.github/WORKFLOWS.md` for detailed workflow documentation.**

## Database Models

Key models in `models.py`:
- **User** - User authentication and profiles (UserRole enum: ADMIN, TREASURER, ACCOUNTANT, CLERK, AUDITOR)
- **Account** - Financial accounts
- **Transaction** - Transaction records (TransactionType, TransactionStatus enums)
- **Department** - Government departments
- **Budget** - Budget allocations
- **PayrollRecord** - Payroll management
- **UtilityPayment** - Utility payment tracking

## API Integrations

### Stripe Integration
- **File**: `stripe/stripe_helpers.py`
- **Main Function**: `create_stripe_customer(params)`
- **Test**: `python -c "import stripe; print('Stripe SDK version:', stripe.__version__)"`

### Modern Treasury Integration
- **File**: `modern_treasury/modern_treasury_helpers.py`
- **Note**: Uses async patterns with exponential backoff
- **Requires**: API keys in environment variables

## Common Issues and Solutions

1. **Circular import error when initializing database**
   - **Solution**: Run `python main.py` instead of manual db initialization
   - Database tables are created automatically on first run

2. **GUI not working**
   - **Expected**: GUI requires X11 display, won't work in headless environments
   - Don't attempt to run in CI/CD pipelines

3. **Import errors**
   - **Solution**: Run `pip install -r requirements.txt`

4. **Linting issues**
   - **Solution**: Run `black .` to auto-format before other linting

5. **Type checking conflicts**
   - **Issue**: `stripe/main.py` and `modern_treasury/main.py` have duplicate names
   - **Solution**: Exclude one with `--exclude` flag when running mypy

6. **Module not found in tests**
   - **Solution**: Run tests from repository root: `pytest -v`

## Performance Expectations

All operations complete quickly (under 5 minutes):
- Dependency installation: ~20-30 seconds
- Linting: ~0.2-0.3 seconds
- Formatting: ~0.4 seconds
- Type checking: ~0.2 seconds
- Application startup: ~1-3 seconds
- Test suite: ~0.3-0.5 seconds
- Frontend build: ~5-20 seconds

**NEVER CANCEL operations** - they complete quickly enough to wait.

## Security Notes

**Government-grade security requirements:**

- ✅ Never commit API keys or secrets to version control
- ✅ All sensitive configuration uses environment variables
- ✅ Input validation mandatory for all user inputs
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ XSS protection via template escaping
- ✅ CSRF protection via Flask-WTF
- ✅ Password hashing with Werkzeug security
- ✅ Role-based access control (RBAC)
- ✅ Audit logging for all financial operations
- ✅ Session management with secure cookies

**When making changes:**
1. Always validate user inputs
2. Use parameterized queries (ORM handles this)
3. Escape template output (Jinja2 handles this)
4. Log security-relevant actions
5. Follow principle of least privilege
6. Review security implications before committing

## Testing Strategy

### Current State
- Basic test infrastructure exists
- Minimal test coverage currently
- Test files: `test_main.py`, `test_smoke.py`, files in `tests/`

### When Adding Tests
- Use pytest fixtures for database setup
- Use Flask test client for endpoint testing
- Mock external API calls (Stripe, Modern Treasury)
- Test both success and error cases
- Test authorization and authentication

### Example Test Pattern
```python
def test_endpoint(client):
    """Test endpoint returns expected response."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'GOFAP' in response.data
```

## Helpful Tips

1. **Working with the database**: Database is created automatically on first `python main.py` run due to circular import constraints

2. **Default credentials**: Admin user is created on first run - username: `admin`, password: `admin123` (change in production!)

3. **Debugging**: Set `FLASK_DEBUG=True` in environment for detailed error messages and auto-reload

4. **Frontend changes**: Run `npm run watch` for auto-rebuild during development

5. **API testing**: Use tools like curl, Postman, or HTTPie to test API endpoints

6. **Logs**: Application logs to both console and `gofap.log` file

7. **Build artifacts**: `.gitignore` excludes `__pycache__`, `*.pyc`, `node_modules`, etc.

## Additional Resources

- **README.md** - Project overview and features
- **CONTRIBUTING.md** - Contribution guidelines
- **CODE_OF_CONDUCT.md** - Community standards
- **SECURITY.md** - Security policy and reporting
- **.github/WORKFLOWS.md** - Detailed workflow documentation
- **docs/** - Additional documentation

## Support

**Office of Finance, Accounting, and Procurement Services (OFAPS)**
- Phone: (844) 697-7877 ext 6327
- Email: gofap@ofaps.spurs.gov
- Website: gofap.gov

---

**Remember**: This is government financial software - security, compliance, and reliability are paramount. When in doubt, err on the side of caution and implement additional security measures.
