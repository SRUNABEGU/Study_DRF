import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name):
    return stripe.Product.create(name=name)


def create_stripe_price(product_id, amount):
    return stripe.Price.create(
        currency='usd',
        unit_amount=int(amount * 100),
        product=product_id,
    )


def create_stripe_session(price_id):
    session = stripe.checkout.Session.create(
        success_url='http://127.0.0.1:8000/',
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
    )
    return session.id, session.url


def get_session(session_id):
    return stripe.checkout.Session.retrieve(session_id)