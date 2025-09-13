import requests
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class ModernTreasuryClient:
    """Modern Treasury API client for government banking operations"""
    
    def __init__(self, api_key: str, base_url: str = "https://app.moderntreasury.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

def create_modern_treasury_account(api_key: str, account_params: Dict[str, Any]) -> requests.Response:
    """
    Create a Modern Treasury external account
    """
    url = "https://app.moderntreasury.com/api/external_accounts"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=account_params, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully created Modern Treasury account")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating Modern Treasury account: {e}")
        raise

def get_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """
    Get Modern Treasury account details
    """
    url = f"https://app.moderntreasury.com/api/external_accounts/{account_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully retrieved Modern Treasury account: {account_id}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving Modern Treasury account: {e}")
        raise

def update_modern_treasury_account(api_key: str, account_id: str, update_params: Dict[str, Any]) -> requests.Response:
    """
    Update Modern Treasury account
    """
    url = f"https://app.moderntreasury.com/api/external_accounts/{account_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.patch(url, json=update_params, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully updated Modern Treasury account: {account_id}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating Modern Treasury account: {e}")
        raise

def delete_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """
    Delete Modern Treasury account
    """
    url = f"https://app.moderntreasury.com/api/external_accounts/{account_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully deleted Modern Treasury account: {account_id}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting Modern Treasury account: {e}")
        raise

def create_payment(api_key: str, payment_params: Dict[str, Any]) -> requests.Response:
    """
    Create a payment through Modern Treasury
    """
    url = "https://app.moderntreasury.com/api/payment_orders"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payment_params, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully created payment order")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating payment order: {e}")
        raise

async def create_modern_treasury_account_async(api_key: str, account_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async version of create_modern_treasury_account
    """
    url = "https://app.moderntreasury.com/api/external_accounts"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=account_params, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    logger.info(f"Successfully created Modern Treasury account async")
                    return {'success': True, 'account_id': data.get('id'), 'data': data}
                else:
                    error_text = await response.text()
                    logger.error(f"Error creating Modern Treasury account async: {error_text}")
                    return {'success': False, 'error': error_text}
    except Exception as e:
        logger.error(f"Unexpected error in async account creation: {e}")
        return {'success': False, 'error': str(e)}