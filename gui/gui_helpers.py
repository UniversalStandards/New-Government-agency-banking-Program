import logging
import time
import asyncio
from typing import Any, Dict, Optional, Callable
import os
from functools import wraps

# Import the actual helper modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'modern_treasury'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stripe'))

from modern_treasury.modern_treasury_helpers import create_modern_treasury_account_async
from stripe.stripe_helpers import create_stripe_customer_async

# Set logger to display messages based on the LOG_LEVEL environment variable
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Define a simple exponential backoff function
def backoff(start_sleep_time=0.1, factor=2, max_sleep_time=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Failed operation, retrying in {sleep_time}s: {e}")
                    await asyncio.sleep(sleep_time)
                    sleep_time = min(sleep_time * factor, max_sleep_time)
        return wrapper
    return decorator

# Process responses for consistency and to centralize error handling
async def process_response(response: Dict[str, Any], service: str) -> Optional[str]:
    if response.get('success'):
        return response.get(service)
    else:
        logger.error(f"Error processing {service} response: {response.get('error', 'Unknown error')}")
        return None

# Asynchronous account creation for Modern Treasury with validation and exponential backoff
@backoff()
async def create_modern_account(api_key: str, params: Dict[str, Any]) -> Optional[str]:
    response = await create_modern_treasury_account_async(api_key, params)
    return await process_response(response, 'account_id')

# Asynchronous customer creation for Stripe with validation and exponential backoff
@backoff()
async def create_stripe_account(api_key: str, params: Dict[str, Any]) -> Optional[str]:
    customer = await create_stripe_customer_async(api_key, params)
    if customer and hasattr(customer, 'id'):
        return customer.id
    return None

# Synchronous wrapper functions for GUI integration
def create_accounts(service: str, api_key: str = None, params: Dict[str, Any] = None) -> Optional[str]:
    """
    Synchronous wrapper for account creation - used by GUI
    """
    if not api_key:
        api_key = os.environ.get(f'{service.upper()}_API_KEY', 'test_key')
    
    if not params:
        params = get_default_params(service)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(create_accounts_async(service, api_key, params))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in synchronous account creation: {e}")
        return None

# Controller function to route to the correct asynchronous account creation function
async def create_accounts_async(service: str, api_key: str, params: Dict[str, Any]) -> Optional[str]:
    service_creation_map = {
        'modern_treasury': create_modern_account,
        'stripe': create_stripe_account
    }

    if service not in service_creation_map:
        logger.error(f"Invalid service: {service}")
        return None

    if service == 'modern_treasury' and not api_key:
        logger.error("Missing API key for Modern Treasury.")
        return None

    creation_func = service_creation_map[service]
    return await creation_func(api_key, params)

def get_default_params(service: str) -> Dict[str, Any]:
    """Get default parameters for each service"""
    if service == 'modern_treasury':
        return {
            'name': 'Government Account',
            'type': 'checking',
            'description': 'Government operations account',
            'routing_number': '123456789',
            'account_number': '987654321',
            'currency': 'USD',
        }
    elif service == 'stripe':
        return {
            'name': 'Government Entity',
            'email': 'admin@government.gov',
            'phone': '+1-555-GOV-MENT',
            'metadata': {
                'type': 'government',
                'department': 'Treasury'
            }
        }
    else:
        return {}
