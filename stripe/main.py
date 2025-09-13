import stripe
import os
from stripe_helpers import create_stripe_customer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Stripe API key from environment variable
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key_here')

def create_government_customer(name, email, phone=None, address=None, metadata=None):
    """
    Create a Stripe customer for government services
    """
    customer_params = {
        'name': name,
        'email': email,
    }
    
    if phone:
        customer_params['phone'] = phone
        
    if address:
        customer_params['address'] = address
        
    if metadata:
        customer_params['metadata'] = metadata
    
    try:
        # Create a Stripe customer
        customer = create_stripe_customer(customer_params)
        logger.info(f"Successfully created Stripe customer: {customer.id}")
        return customer
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {e}")
        return None

def main():
    """Main function to demonstrate Stripe customer creation"""
    # Define parameters for customer creation
    customer_params = {
        'name': 'Government Employee',
        'email': 'employee@government.gov',
        'phone': '+1-555-123-4567',
        'address': {
            'line1': '123 Government Street',
            'line2': 'Suite 100',
            'city': 'Washington',
            'state': 'DC',
            'postal_code': '20001',
            'country': 'US'
        },
        'metadata': {
            'employee_id': 'GOV001',
            'department': 'Treasury',
            'role': 'Financial Officer'
        }
    }
    
    # Create a Stripe customer
    customer = create_government_customer(**customer_params)
    
    if customer:
        print(f"Customer created successfully with ID: {customer.id}")
        return customer
    else:
        print("Failed to create customer")
        return None

if __name__ == "__main__":
    main()