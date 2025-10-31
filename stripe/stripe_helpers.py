"""Stripe integration helpers for GOFAP payment processing."""

import asyncio
import logging
from typing import Any, Dict

import stripe
from configs.settings import STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

class StripePaymentProcessor:
    """Stripe payment processor for government payments."""

    def __init__(self, api_key: str = None):
        if api_key:
            stripe.api_key = api_key

        if not stripe.api_key:
            logger.warning("Stripe API key not configured")

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=customer_data["email"],
                name=customer_data.get("name"),
                phone=customer_data.get("phone"),
                description=customer_data.get("description", "GOFAP Customer"),
                metadata=customer_data.get("metadata", {}),
            )

            logger.info(f"Stripe customer created: {customer.id}")
            return customer

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        customer_id: str = None,
        description: str = None,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a payment intent for utility payments or other government fees."""
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                customer=customer_id,
                description=description or "Government payment",
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
                statement_descriptor_suffix="GOFAP",
            )

            logger.info(f"Payment intent created: {payment_intent.id}")
            return payment_intent

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise

def create_stripe_customer(params):
    """Synchronous function to create Stripe customer."""
    return stripe.Customer.create(**params)

async def create_stripe_customer_async(
    api_key: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """Asynchronous function to create Stripe customer."""
    stripe.api_key = api_key

    try:
        # Use asyncio to run the synchronous Stripe call
        loop = asyncio.get_event_loop()
        customer = await loop.run_in_executor(None, create_stripe_customer, params)

        return {
            "success": True,
            "id": customer.id,
            "data": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "created": customer.created,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def create_stripe_customer(params):
    """Create a Stripe customer."""
    return stripe.Customer.create(**params)

async def create_stripe_customer_async(
    api_key: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """Async version of Stripe customer creation."""
    try:
        stripe.api_key = api_key
        customer = create_stripe_customer(params)
        return {"success": True, "id": customer.id}
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {e}")
        return {"success": False, "error": str(e)}
    return stripe.Customer.create(**params)
