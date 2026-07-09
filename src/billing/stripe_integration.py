"""
Stripe Integration - Payment processing for SaaS billing
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class StripeIntegration:
    """
    Integrates with Stripe for payment processing.
    Handles subscription creation, invoice payment, and webhooks.
    """

    def __init__(self, api_key: str | None = None, webhook_secret: str | None = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        if not self.api_key:
            logger.warning("STRIPE_API_KEY not set - running in mock mode")
            self.mock_mode = True
        else:
            try:
                import stripe

                stripe.api_key = self.api_key
                self.stripe = stripe
                self.mock_mode = False
            except ImportError:
                logger.warning("stripe package not installed - mock mode")
                self.mock_mode = True

    def create_customer(self, tenant_id: str, email: str, name: str) -> dict[str, Any]:
        """Create a Stripe customer for a tenant."""
        if self.mock_mode:
            return {"id": f"cus_mock_{tenant_id}", "email": email, "mock": True}
        try:
            customer = self.stripe.Customer.create(
                email=email, name=name, metadata={"tenant_id": tenant_id}
            )
            return {"id": customer.id, "email": customer.email}
        except Exception as e:
            logger.error(f"Stripe customer creation failed: {e}")
            raise

    def create_subscription(
        self, customer_id: str, price_id: str, metadata: dict | None = None
    ) -> dict[str, Any]:
        """Create a subscription for a tenant."""
        if self.mock_mode:
            return {"id": f"sub_mock_{customer_id}", "status": "active", "mock": True}
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id, items=[{"price": price_id}], metadata=metadata or {}
            )
            return {"id": subscription.id, "status": subscription.status}
        except Exception as e:
            logger.error(f"Stripe subscription failed: {e}")
            raise

    def create_invoice_item(
        self, customer_id: str, amount: float, currency: str = "usd", description: str = ""
    ) -> dict[str, Any]:
        """Create an invoice item (for metered usage)."""
        if self.mock_mode:
            return {"id": f"ii_mock_{customer_id}", "amount": amount, "mock": True}
        try:
            item = self.stripe.InvoiceItem.create(
                customer=customer_id,
                amount=int(amount * 100),  # cents
                currency=currency,
                description=description,
            )
            return {"id": item.id, "amount": item.amount}
        except Exception as e:
            logger.error(f"Stripe invoice item failed: {e}")
            raise

    def create_payment_intent(
        self, amount: float, currency: str = "usd", metadata: dict | None = None
    ) -> dict[str, Any]:
        """Create payment intent for one-time charges."""
        if self.mock_mode:
            return {"id": f"pi_mock_{amount}", "client_secret": "mock_secret", "mock": True}
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100), currency=currency, metadata=metadata or {}
            )
            return {"id": intent.id, "client_secret": intent.client_secret}
        except Exception as e:
            logger.error(f"Stripe payment intent failed: {e}")
            raise

    def verify_webhook(self, payload: bytes, signature: str) -> dict[str, Any]:
        """Verify and parse Stripe webhook."""
        if self.mock_mode:
            return {"mock": True, "type": "mock.event"}
        try:
            event = self.stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return event
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            raise ValueError("Invalid webhook signature")

    def handle_webhook_event(self, event: dict[str, Any]) -> str:
        """Process Stripe webhook events."""
        event_type = event.get("type", "")
        if event_type == "invoice.paid":
            return "invoice_paid"
        elif event_type == "invoice.payment_failed":
            return "payment_failed"
        elif event_type == "customer.subscription.deleted":
            return "subscription_canceled"
        return "unhandled"
