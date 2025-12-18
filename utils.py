"""
Utility functions for GOFAP application.
"""

import logging

logger = logging.getLogger(__name__)


def safe_error_response(exception: Exception, default_message: str = "An error occurred") -> str:
    """
    Safely handle exceptions by logging the full error and returning a generic message.
    
    This prevents information exposure through exception messages by:
    - Logging the full exception details for debugging
    - Returning a safe, generic error message to users
    
    Args:
        exception: The exception that was caught
        default_message: Generic message to return to users (default: "An error occurred")
    
    Returns:
        A safe, generic error message string
    """
    # Log the full exception details for internal debugging
    logger.error(f"Error occurred: {type(exception).__name__}: {str(exception)}", exc_info=True)
    
    # Return a generic message that doesn't expose internal details
    return default_message
