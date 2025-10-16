"""
Test cases for GUI helper functions.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add parent directory to path to import gui modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gui.gui_helpers import create_accounts, create_accounts_async


class TestCreateAccountsFunctions:
    """Test that create_accounts functions are properly separated."""

    def test_async_function_exists(self):
        """Test that create_accounts_async exists and is async."""
        assert asyncio.iscoroutinefunction(create_accounts_async)

    def test_sync_function_exists(self):
        """Test that create_accounts exists and is not async."""
        assert not asyncio.iscoroutinefunction(create_accounts)

    @pytest.mark.asyncio
    async def test_async_function_calls_correct_service(self):
        """Test that create_accounts_async routes to correct service function."""
        # Mock the service-specific functions
        with patch("gui.gui_helpers.create_modern_account", new_callable=AsyncMock) as mock_modern:
            mock_modern.return_value = "test_account_id"

            result = await create_accounts_async(
                "modern_treasury", "test_api_key", {"name": "Test"}
            )

            # Verify the modern treasury function was called
            mock_modern.assert_called_once_with("test_api_key", {"name": "Test"})
            assert result == "test_account_id"

    def test_sync_function_no_recursion(self):
        """Test that synchronous create_accounts doesn't cause infinite recursion."""
        # Mock the async function to prevent actual API calls
        with patch("gui.gui_helpers.create_accounts_async", new_callable=AsyncMock) as mock_async:
            mock_async.return_value = "test_result"

            result = create_accounts("stripe", "test_key", {"email": "test@example.com"})

            # Verify that create_accounts_async was called (not create_accounts itself)
            mock_async.assert_called_once()
            assert result == "test_result"

    def test_sync_function_default_params(self):
        """Test that synchronous create_accounts uses default params."""
        with patch("gui.gui_helpers.create_accounts_async", new_callable=AsyncMock) as mock_async:
            mock_async.return_value = "test_result"

            # Call without params
            result = create_accounts("stripe")

            # Verify default params were used
            call_args = mock_async.call_args
            assert call_args is not None
            # Check that params were passed (should be default dict)
            assert "name" in call_args[0][2]
            assert "email" in call_args[0][2]

    def test_sync_function_error_handling(self):
        """Test that synchronous create_accounts handles errors gracefully."""
        with patch("gui.gui_helpers.create_accounts_async", new_callable=AsyncMock) as mock_async:
            mock_async.side_effect = Exception("Test error")

            result = create_accounts("stripe", "test_key", {"email": "test@example.com"})

            # Should return None on error, not raise exception
            assert result is None
