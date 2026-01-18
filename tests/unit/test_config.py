"""Unit tests for configuration settings."""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

from configs.settings import APP_NAME, DEBUG, SECRET_KEY, VERSION, get_config

def test_debug_configuration():
    """Test DEBUG configuration is properly loaded."""
    assert isinstance(DEBUG, bool)

def test_app_constants():
    """Test application constants are properly set."""
    assert APP_NAME == "Government Operations and Financial Accounting Platform (GOFAP)"
    assert VERSION == "1.0.0"

def test_get_config_function():
    """Test the get_config utility function."""
    # Test with existing environment variable
    test_value = get_config("PATH")
    assert test_value is not None

    # Test with default value
    test_default = get_config("NON_EXISTENT_VAR", "default_value")
    assert test_default == "default_value"

    # Test with None default
    test_none = get_config("NON_EXISTENT_VAR")
    assert test_none is None

def test_environment_variable_loading():
    """Test that environment variables are properly loaded."""
    # Test setting a temporary environment variable
    os.environ["TEST_CONFIG_VAR"] = "test_value"

    result = get_config("TEST_CONFIG_VAR")
    assert result == "test_value"

    # Clean up
    del os.environ["TEST_CONFIG_VAR"]

def test_import_without_secret_key():
    """
    Test that configs.settings can be imported without SECRET_KEY environment variable.

    This is critical for auxiliary scripts (gui/gui_main.py, modern_treasury_helpers.py, etc.)
    that only need API keys and constants, not Flask secrets.

    Regression test for: https://github.com/UniversalStandards/New-Government-agency-banking-Program/issues/294
    """
    # Run a subprocess without SECRET_KEY to ensure import works
    test_code = textwrap.dedent(f"""
        import os
        import sys

        # Ensure SECRET_KEY is not in environment
        os.environ.pop('SECRET_KEY', None)

        # This should NOT raise ValueError
        from configs import settings

        # Verify we got the default value
        assert settings.SECRET_KEY == '{SECRET_KEY}', f"Expected default SECRET_KEY, got: {{settings.SECRET_KEY}}"

        # Verify we can access API keys
        assert hasattr(settings, 'STRIPE_SECRET_KEY'), "Should have STRIPE_SECRET_KEY"
        assert hasattr(settings, 'MODERN_TREASURY_API_KEY'), "Should have MODERN_TREASURY_API_KEY"

        print("SUCCESS")
        """)

    # Get project root directory (3 levels up from this test file)
    project_root = Path(__file__).parent.parent.parent

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert (
        "SUCCESS" in result.stdout
    ), f"Test did not complete successfully: {result.stdout}"

def test_secret_key_has_default():
    """Test that SECRET_KEY always has a default value to prevent import-time errors."""
    from configs import settings

    # SECRET_KEY should never be None or empty string
    assert settings.SECRET_KEY is not None
    assert settings.SECRET_KEY != ""
    assert isinstance(settings.SECRET_KEY, str)

def test_validate_config_not_called_at_import():
    """
    Test that validate_config() is not called automatically at module import time.

    This ensures auxiliary scripts can import the module without triggering
    production-level validation checks.
    """
    # If validate_config() were called at import time in production mode,
    # it would raise an error. Since we can import in tests, it's not being called.
    from configs import settings

    # validate_config should be a callable function
    assert callable(settings.validate_config)

    # In development mode, calling it should succeed
    if settings.is_development():
        result = settings.validate_config()
        assert result is True
