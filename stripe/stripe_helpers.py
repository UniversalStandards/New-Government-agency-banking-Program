import stripe
import logging

# Set up logging
logger = logging.getLogger(__name__)

def create_stripe_customer(params):
    """
    Create a Stripe customer with error handling
    """
    try:
        customer = stripe.Customer.create(**params)
        logger.info(f"Successfully created Stripe customer: {customer.id}")
        return customer
    except stripe.error.CardError as e:
        logger.error(f"Card error: {e.user_message}")
        raise
    except stripe.error.RateLimitError as e:
        logger.error("Rate limit error - too many requests made to the API too quickly")
        raise
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid parameters: {e.user_message}")
        raise
    except stripe.error.AuthenticationError as e:
        logger.error("Authentication error - check your API keys")
        raise
    except stripe.error.APIConnectionError as e:
        logger.error("Network communication error")
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def create_payment_intent(amount, currency='usd', customer_id=None, metadata=None):
    """
    Create a Stripe payment intent for government transactions
    """
    params = {
        'amount': int(amount * 100),  # Convert to cents
        'currency': currency,
        'automatic_payment_methods': {
            'enabled': True,
        },
    }
    
    if customer_id:
        params['customer'] = customer_id
        
    if metadata:
        params['metadata'] = metadata
    
    try:
        intent = stripe.PaymentIntent.create(**params)
        logger.info(f"Successfully created payment intent: {intent.id}")
        return intent
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise

def create_account(params):
    """
    Create a Stripe Connect account for government entities
    """
    try:
        account = stripe.Account.create(**params)
        logger.info(f"Successfully created Stripe account: {account.id}")
        return account
    except Exception as e:
        logger.error(f"Error creating Stripe account: {e}")
        raise

async def create_stripe_customer_async(api_key, params):
    """
    Async version of create_stripe_customer for use with async frameworks
    """
    stripe.api_key = api_key
    return create_stripe_customer(params)