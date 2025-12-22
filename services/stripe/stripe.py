import os
from typing import Any, Dict, Optional

import stripe
from utils import safe_error_response

from ..service import Service

class StripeService(Service):
    """Complete Stripe payment service implementation."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        stripe.api_key = self.api_key

    def get_api_key(self) -> str:
        """Get Stripe API key from environment."""
        api_key = (
            os.environ.get("STRIPE_SECRET_KEY")
            or os.environ.get("STRIPE_API_KEY")
            or ""
        )
        return api_key

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(**customer_data)
            return {"success": True, "customer_id": customer.id, "data": customer}
        except stripe.error.StripeError as e:
            error_msg = safe_error_response(e, "Failed to create customer")
            return {"success": False, "error": error_msg}

    def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a payment through Stripe."""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=payment_data["amount"],
                currency=payment_data.get("currency", "usd"),
                customer=payment_data.get("customer_id"),
                payment_method=payment_data.get("payment_method"),
                confirm=payment_data.get("confirm", True),
            )
            return {
                "success": True,
                "payment_id": payment_intent.id,
                "status": payment_intent.status,
                "data": payment_intent,
            }
        except stripe.error.StripeError as e:
            error_msg = safe_error_response(e, "Payment processing failed")
            return {"success": False, "error": error_msg}

    def get_balance(self, account_id: str = None) -> Dict[str, Any]:
        """Get Stripe account balance."""
        try:
            balance = stripe.Balance.retrieve()
            return {
                "success": True,
                "available": balance.available,
                "pending": balance.pending,
            }
        except stripe.error.StripeError as e:
            error_msg = safe_error_response(e, "Failed to retrieve balance")
            return {"success": False, "error": error_msg}

    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Stripe Connect account."""
        try:
            account = stripe.Account.create(
                type=account_data.get("type", "express"),
                country=account_data.get("country", "US"),
                email=account_data.get("email"),
                capabilities=account_data.get(
                    "capabilities",
                    {
                        "card_payments": {"requested": True},
                        "transfers": {"requested": True},
                    },
                ),
            )
            return {"success": True, "account_id": account.id, "data": account}
        except stripe.error.StripeError as e:
            error_msg = safe_error_response(e, "Failed to create account")
            return {"success": False, "error": error_msg}

    def create_payment_method(
        self, payment_method_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a payment method."""
        try:
            payment_method = stripe.PaymentMethod.create(**payment_method_data)
            return {
                "success": True,
                "payment_method_id": payment_method.id,
                "data": payment_method,
            }
        except stripe.error.StripeError as e:
            error_msg = safe_error_response(e, "Failed to create payment method")
            return {"success": False, "error": error_msg}
