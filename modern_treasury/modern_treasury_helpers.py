"""Modern Treasury integration helpers for GOFAP."""

import requests
import logging
from typing import Dict, Any
from configs.settings import MODERN_TREASURY_API_KEY, MODERN_TREASURY_ORG_ID

logger = logging.getLogger(__name__)


class ModernTreasuryClient:
    """Client for Modern Treasury API integration."""
    
    def __init__(self, api_key: str = None, org_id: str = None):
        self.api_key = api_key or MODERN_TREASURY_API_KEY
        self.org_id = org_id or MODERN_TREASURY_ORG_ID
        self.base_url = "https://app.moderntreasury.com/api"
        
        if not self.api_key:
            logger.warning("Modern Treasury API key not configured")
    
    def _make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
        """Make authenticated request to Modern Treasury API."""
        if not self.api_key:
            raise ValueError("Modern Treasury API key not configured")
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Modern Treasury API request failed: {e}")
            raise
    
    def create_external_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an external account in Modern Treasury."""
        return self._make_request("POST", "/external_accounts", account_data)
    
    def create_payment_order(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment order."""
        return self._make_request("POST", "/payment_orders", payment_data)
    
    def get_payment_orders(self, limit: int = 25) -> Dict[str, Any]:
        """Get payment orders."""
        return self._make_request("GET", f"/payment_orders?limit={limit}")
    
    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """Get account balance from Modern Treasury."""
        return self._make_request("GET", f"/external_accounts/{account_id}/balances")
    
    def create_ledger_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ledger transaction."""
        return self._make_request("POST", "/ledger_transactions", transaction_data)
    
    def get_ledger_accounts(self) -> Dict[str, Any]:
        """Get ledger accounts."""
        return self._make_request("GET", "/ledger_accounts")


def process_government_payment(
    amount: float,
    recipient_account: str,
    description: str,
    payment_type: str = "ach"
) -> Dict[str, Any]:
    """
    Process a government payment using Modern Treasury.
    
    Args:
        amount: Payment amount
        recipient_account: Recipient account details
        description: Payment description
        payment_type: Type of payment (ach, wire, etc.)
    
    Returns:
        Payment processing result
    """
    try:
        client = ModernTreasuryClient()
        
        payment_data = {
            "type": payment_type,
            "amount": int(amount * 100),  # Convert to cents
            "currency": "USD",
            "direction": "credit",
            "description": description,
            "receiving_account_id": recipient_account,
            "metadata": {
                "source": "GOFAP",
                "payment_category": "government_payment"
            }
        }
        
        result = client.create_payment_order(payment_data)
        logger.info(f"Payment order created: {result.get('id')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process government payment: {e}")
        raise


def setup_payroll_account(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up a payroll account for an employee.
    
    Args:
        employee_data: Employee information
    
    Returns:
        Account creation result
    """
    try:
        client = ModernTreasuryClient()
        
        account_data = {
            "name": f"{employee_data['first_name']} {employee_data['last_name']} Payroll",
            "account_type": "checking",
            "party_name": f"{employee_data['first_name']} {employee_data['last_name']}",
            "party_type": "person",
            "routing_number": employee_data.get('routing_number'),
            "account_number": employee_data.get('account_number'),
            "metadata": {
                "employee_id": str(employee_data['employee_id']),
                "department": employee_data.get('department', ''),
                "account_purpose": "payroll"
            }
        }
        
        result = client.create_external_account(account_data)
        logger.info(f"Payroll account created: {result.get('id')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to setup payroll account: {e}")
        raise


def bulk_payroll_processing(payroll_records: list) -> Dict[str, Any]:
    """
    Process bulk payroll payments.
    
    Args:
        payroll_records: List of payroll records to process
    
    Returns:
        Bulk processing result
    """
    try:
        client = ModernTreasuryClient()
        results = []
        
        for record in payroll_records:
            payment_data = {
                "type": "ach",
                "amount": int(record['net_pay'] * 100),  # Convert to cents
                "currency": "USD",
                "direction": "credit",
                "description": f"Payroll - {record['pay_period_start']} to {record['pay_period_end']}",
                "receiving_account_id": record['account_id'],
                "metadata": {
                    "employee_id": str(record['employee_id']),
                    "payroll_period": f"{record['pay_period_start']}_to_{record['pay_period_end']}",
                    "gross_pay": record['gross_pay'],
                    "net_pay": record['net_pay']
                }
            }
            
            result = client.create_payment_order(payment_data)
            results.append(result)
        
        logger.info(f"Processed {len(results)} payroll payments")
        return {"processed_count": len(results), "results": results}
        
    except Exception as e:
        logger.error(f"Failed to process bulk payroll: {e}")
        raise
"""
Modern Treasury API helper functions for GOFAP.
Provides comprehensive integration with Modern Treasury for government financial operations.
"""

import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

class ModernTreasuryError(Exception):
    """Custom exception for Modern Treasury API errors."""

class ModernTreasuryClient:
    """Client for interacting with Modern Treasury API."""

    def __init__(self, api_key: str, organization_id: str):
        self.api_key = api_key
        self.organization_id = organization_id
        self.base_url = "https://app.moderntreasury.com/api"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Organization-Id": organization_id,
        }

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Modern Treasury API."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, json=data, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Modern Treasury API error: {e}")
            raise ModernTreasuryError(f"API request failed: {e}")

    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new account in Modern Treasury."""
        return self._make_request("POST", "/accounts", account_data)

    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get account details by ID."""
        return self._make_request("GET", f"/accounts/{account_id}")

    def update_account(
        self, account_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update account details."""
        return self._make_request("PATCH", f"/accounts/{account_id}", update_data)

    def delete_account(self, account_id: str) -> Dict[str, Any]:
        """Delete an account."""
        return self._make_request("DELETE", f"/accounts/{account_id}")

    def list_accounts(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """List all accounts with optional filtering."""
        query_params = "&".join([f"{k}={v}" for k, v in (params or {}).items()])
        endpoint = f"/accounts?{query_params}" if query_params else "/accounts"
        return self._make_request("GET", endpoint)

    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new payment."""
        return self._make_request("POST", "/payments", payment_data)

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details by ID."""
        return self._make_request("GET", f"/payments/{payment_id}")

    def list_payments(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """List all payments with optional filtering."""
        query_params = "&".join([f"{k}={v}" for k, v in (params or {}).items()])
        endpoint = f"/payments?{query_params}" if query_params else "/payments"
        return self._make_request("GET", endpoint)

    def create_external_account(
        self, external_account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an external account (bank account, card, etc.)."""
        return self._make_request("POST", "/external_accounts", external_account_data)

    def get_external_account(self, external_account_id: str) -> Dict[str, Any]:
        """Get external account details by ID."""
        return self._make_request("GET", f"/external_accounts/{external_account_id}")

    def list_external_accounts(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """List all external accounts with optional filtering."""
        query_params = "&".join([f"{k}={v}" for k, v in (params or {}).items()])
        endpoint = (
            f"/external_accounts?{query_params}"
            if query_params
            else "/external_accounts"
        )
        return self._make_request("GET", endpoint)

# Legacy function wrappers for backward compatibility
def create_modern_treasury_account(
    api_key: str, account_params: Dict[str, Any]
) -> requests.Response:
    """Legacy function to create Modern Treasury account."""
    client = ModernTreasuryClient(api_key, account_params.get("organization_id", ""))
    try:
        result = client.create_account(account_params)

        # Create a mock response object for backward compatibility
        class MockResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        return MockResponse(result)
    except ModernTreasuryError as e:
        logger.error(f"Failed to create account: {e}")
        raise

def get_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """Legacy function to get Modern Treasury account."""
    client = ModernTreasuryClient(api_key, "")
    try:
        result = client.get_account(account_id)

        class MockResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        return MockResponse(result)
    except ModernTreasuryError as e:
        logger.error(f"Failed to get account: {e}")
        raise

def update_modern_treasury_account(
    api_key: str, account_id: str, update_params: Dict[str, Any]
) -> requests.Response:
    """Legacy function to update Modern Treasury account."""
    client = ModernTreasuryClient(api_key, "")
    try:
        result = client.update_account(account_id, update_params)

        class MockResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        return MockResponse(result)
    except ModernTreasuryError as e:
        logger.error(f"Failed to update account: {e}")
        raise

def delete_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """Legacy function to delete Modern Treasury account."""
    client = ModernTreasuryClient(api_key, "")
    try:
        result = client.delete_account(account_id)

        class MockResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        return MockResponse(result)
    except ModernTreasuryError as e:
        logger.error(f"Failed to delete account: {e}")
        raise

# Async versions for modern usage
async def create_modern_treasury_account_async(
    api_key: str, account_params: Dict[str, Any]
) -> Dict[str, Any]:
    """Async function to create Modern Treasury account."""
    import aiohttp

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Organization-Id": account_params.get("organization_id", ""),
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://app.moderntreasury.com/api/accounts",
                headers=headers,
                json=account_params,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "account_id": data.get("id"), "data": data}
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Modern Treasury API base URL
MT_BASE_URL = "https://app.moderntreasury.com/api"

def create_modern_treasury_account(
    api_key: str, account_params: Dict[str, Any]
) -> requests.Response:
    """Create a Modern Treasury account."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{MT_BASE_URL}/external_accounts"
    response = requests.post(url, json=account_params, headers=headers, timeout=10)
    return response

def get_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """Get a Modern Treasury account by ID."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{MT_BASE_URL}/external_accounts/{account_id}"
    response = requests.get(url, headers=headers)
    return response

def update_modern_treasury_account(
    api_key: str, account_id: str, update_params: Dict[str, Any]
) -> requests.Response:
    """Update a Modern Treasury account."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{MT_BASE_URL}/external_accounts/{account_id}"
    response = requests.patch(url, json=update_params, headers=headers)
    return response

def delete_modern_treasury_account(api_key: str, account_id: str) -> requests.Response:
    """Delete a Modern Treasury account."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{MT_BASE_URL}/external_accounts/{account_id}"
    response = requests.delete(url, headers=headers)
    return response

async def create_modern_treasury_account_async(
    api_key: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """Async version of Modern Treasury account creation."""
    try:
        # Simulate async operation - in real implementation, use aiohttp
        response = create_modern_treasury_account(api_key, params)
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "account_id": response.json().get("id", ""),
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
            }
    except Exception as e:
        logger.error(f"Error creating Modern Treasury account: {e}")
        return {"success": False, "error": str(e)}
