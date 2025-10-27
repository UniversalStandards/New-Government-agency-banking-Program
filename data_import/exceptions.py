"""
Custom exceptions for the data import module.
"""

class ImportError(Exception):
    """Base exception for data import operations."""

class SyncError(ImportError):
    """Exception raised when synchronization fails."""

class ConfigurationError(ImportError):
    """Exception raised when configuration is invalid or missing."""

class AuthenticationError(ImportError):
    """Exception raised when authentication fails."""

class RateLimitError(ImportError):
    """Exception raised when API rate limits are exceeded."""

class DataValidationError(ImportError):
    """Exception raised when imported data fails validation."""
