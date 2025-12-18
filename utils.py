"""
Utility functions for GOFAP application.
"""

import logging

logger = logging.getLogger(__name__)


def safe_error_response(exception: Exception, default_message: str = "An error occurred") -> str:
    """
    Safely handle exceptions by logging the full error and returning a generic message.

    This prevents information exposure through exception messages by:
    - Logging exception type and traceback for debugging
    - Returning a safe, generic error message to users
    - Not logging full exception message to protect sensitive data in shared logs

    Args:
        exception: The exception that was caught
        default_message: Generic message to return to users (default: "An error occurred")

    Returns:
        A safe, generic error message string

    Security Note:
        Exception details are logged with exc_info=True for server-side debugging.
        Ensure log files have appropriate access controls and are not exposed publicly.
    """
    # Log exception type and stack trace for debugging without exposing in the message
    # The exc_info=True provides the full traceback without putting sensitive data in the log message
    logger.error(f"Error occurred: {type(exception).__name__}", exc_info=True)

    # Return a generic message that doesn't expose internal details
    return default_message
