import os

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
"""Configuration settings for GOFAP (Government Operations and Financial Accounting Platform)."""

import os
from datetime import timedelta
from typing import Any

# Environment detection
ENVIRONMENT = os.environ.get("FLASK_ENV", "development")

# Debug mode setting
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes", "on")

# Database configuration
DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///gofap.db")
# Fix for SQLAlchemy 2.0+ compatibility - replace postgres:// with postgresql://
if DATABASE_URI and DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

# API Configuration
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

MODERN_TREASURY_API_KEY = os.environ.get("MODERN_TREASURY_API_KEY", "")
MODERN_TREASURY_ORG_ID = os.environ.get("MODERN_TREASURY_ORG_ID", "")
MODERN_TREASURY_WEBHOOK_SECRET = os.environ.get("MODERN_TREASURY_WEBHOOK_SECRET", "")

# Security configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE", "gofap.log")

# Email configuration
MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@gofap.gov")

# File upload configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv", "xlsx"}

# Pagination configuration
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate limiting
RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
RATELIMIT_DEFAULT = "100 per hour"

# Cache configuration
CACHE_TYPE = os.environ.get("CACHE_TYPE", "simple")
CACHE_DEFAULT_TIMEOUT = 300

# Application configuration
APP_NAME = "Government Operations and Financial Accounting Platform (GOFAP)"
VERSION = "1.0.0"
DESCRIPTION = "Comprehensive financial management platform for government operations"

# Feature flags
ENABLE_REGISTRATION = os.environ.get("ENABLE_REGISTRATION", "true").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
ENABLE_API = os.environ.get("ENABLE_API", "true").lower() in ("true", "1", "yes", "on")
ENABLE_ANALYTICS = os.environ.get("ENABLE_ANALYTICS", "true").lower() in (
    "true",
    "1",
    "yes",
    "on",
)

# External service endpoints
STRIPE_API_BASE = "https://api.stripe.com/v1"
MODERN_TREASURY_API_BASE = "https://app.moderntreasury.com/api"

# Default currency
DEFAULT_CURRENCY = "USD"

# Audit configuration
AUDIT_LOG_RETENTION_DAYS = int(os.environ.get("AUDIT_LOG_RETENTION_DAYS", 365))

# Backup configuration
BACKUP_ENABLED = os.environ.get("BACKUP_ENABLED", "false").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
BACKUP_SCHEDULE = os.environ.get("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
MODERN_TREASURY_API_KEY = os.environ.get("MODERN_TREASURY_API_KEY", "")
MODERN_TREASURY_ORG_ID = os.environ.get("MODERN_TREASURY_ORG_ID", "")

# Security configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

# Application configuration
APP_NAME = "Government Operations and Financial Accounting Platform (GOFAP)"
VERSION = "1.0.0"

# Data import settings
LINEAR_API_KEY = os.environ.get("LINEAR_API_KEY")
LINEAR_WORKSPACE_ID = os.environ.get("LINEAR_WORKSPACE_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = os.environ.get("GITHUB_ORG")

# Sync settings
SYNC_INTERVAL_MINUTES = int(os.environ.get("SYNC_INTERVAL_MINUTES", "60"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", "30"))

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE")

# Data import settings
LINEAR_API_KEY = os.environ.get("LINEAR_API_KEY")
LINEAR_WORKSPACE_ID = os.environ.get("LINEAR_WORKSPACE_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = os.environ.get("GITHUB_ORG")

# Sync settings
SYNC_INTERVAL_MINUTES = int(os.environ.get("SYNC_INTERVAL_MINUTES", "60"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", "30"))

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE")

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value with fallback to default."""
    return os.environ.get(key, default)

def is_production() -> bool:
    """Check if running in production environment."""
    return ENVIRONMENT == "production"

def is_development() -> bool:
    """Check if running in development environment."""
    return ENVIRONMENT == "development"

def is_testing() -> bool:
    """Check if running in testing environment."""
    return ENVIRONMENT == "testing"

# Configuration validation
def validate_config():
    """Validate configuration settings."""
    errors = []

    if is_production() and SECRET_KEY == os.environ.get("DEV_SECRET_KEY"):
        errors.append("SECRET_KEY must be changed in production")

    if is_production() and not SESSION_COOKIE_SECURE:
        errors.append("SESSION_COOKIE_SECURE must be True in production")

    if not DATABASE_URI:
        errors.append("DATABASE_URI is required")

    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

    return True
