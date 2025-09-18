"""Modern Treasury integration helpers for GOFAP."""

import requests
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