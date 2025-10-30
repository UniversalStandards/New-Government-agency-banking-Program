"""Unit tests for configuration settings."""

import os

from configs.settings import APP_NAME, DEBUG, VERSION, get_config

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
