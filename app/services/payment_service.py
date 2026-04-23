"""Payment service — tokenized, PCI DSS compliant (no card data stored)."""
import uuid
import hashlib
from datetime import datetime, timezone


class PaymentService:
    """Simulated payment gateway using tokenization.

    In production this would integrate with Stripe/PayPal.
    No raw card data is ever stored — only a payment token.
    """

    @staticmethod
    def create_payment_token(card_last_four: str, amount: float) -> str:
        """Generate a unique payment token (simulated gateway call)."""
        raw = f"{card_last_four}-{amount}-{datetime.now(timezone.utc).isoformat()}"
        token = f"tok_{hashlib.sha256(raw.encode()).hexdigest()[:24]}_{uuid.uuid4().hex[:8]}"
        return token

    @staticmethod
    def process_payment(token: str, amount: float) -> dict:
        """Simulate payment processing via gateway."""
        # In production: call Stripe/PayPal API with the token
        return {
            'success': True,
            'token': token,
            'amount': amount,
            'message': 'Pago procesado correctamente',
        }

    @staticmethod
    def validate_card_input(card_number: str) -> dict:
        """Basic client-side-style validation (no storage)."""
        clean = card_number.replace(' ', '').replace('-', '')
        if not clean.isdigit() or len(clean) not in (13, 14, 15, 16):
            return {'valid': False, 'error': 'Número de tarjeta inválido'}
        return {'valid': True, 'last_four': clean[-4:]}
