from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from db import log_usage, log_transaction, get_skill

DEVELOPER_SHARE = 0.80
PLATFORM_SHARE = 0.20


class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, skill_id: str, agent_id: str, amount: float) -> dict:
        pass

    @abstractmethod
    def generate_proof(self, skill_id: str, agent_id: str) -> str:
        pass


def _make_proof(skill_id: str, agent_id: str) -> str:
    nonce = uuid.uuid4().hex
    ts = datetime.now(timezone.utc).isoformat()
    return hashlib.sha256(f"{skill_id}:{agent_id}:{ts}:{nonce}".encode()).hexdigest()


def _build_txn(skill_id: str, agent_id: str, amount: float, proof_hash: str, gateway: str) -> dict:
    txn_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    dev = round(amount * DEVELOPER_SHARE, 4)  # type: ignore[no-matching-overload]
    plat = round(amount * PLATFORM_SHARE, 4)  # type: ignore[no-matching-overload]
    log_transaction({
        "transaction_id": txn_id, "skill_id": skill_id, "agent_id": agent_id,
        "total_amount": amount, "developer_share": dev,
        "platform_share": plat, "proof_hash": proof_hash,
    })
    return {
        "status": "completed",
        "transaction_id": txn_id,
        "proof_of_execution": proof_hash,
        "developer_payout": dev,
        "platform_fee": plat,
        "timestamp": ts,
        "gateway": gateway,
    }


class MockPaymentGateway(PaymentGateway):
    """Local mock — logs transactions to SQLite. No real money moves."""

    def generate_proof(self, skill_id: str, agent_id: str) -> str:
        return _make_proof(skill_id, agent_id)

    def process_payment(self, skill_id: str, agent_id: str, amount: float) -> dict:
        proof = self.generate_proof(skill_id, agent_id)
        return _build_txn(skill_id, agent_id, amount, proof, "mock")


class StripePaymentGateway(PaymentGateway):
    """
    Stripe-shaped stub. Mirrors the Stripe PaymentIntent API response.
    Set STRIPE_SECRET_KEY env var to enable real Stripe charging.
    """

    def __init__(self) -> None:
        self.api_key = os.environ.get("STRIPE_SECRET_KEY")

    def generate_proof(self, skill_id: str, agent_id: str) -> str:
        return _make_proof(skill_id, agent_id)

    def process_payment(self, skill_id: str, agent_id: str, amount: float) -> dict:
        proof = self.generate_proof(skill_id, agent_id)

        if not self.api_key:
            # No key — return a Stripe-shaped stub response
            txn = _build_txn(skill_id, agent_id, amount, proof, "stripe_stub")
            txn["stripe"] = {
                "id": "pi_" + uuid.uuid4().hex[0:24],  # type: ignore[no-matching-overload]
                "object": "payment_intent",
                "amount": int(amount * 100),
                "currency": "usd",
                "status": "succeeded",
                "metadata": {"skill_id": skill_id, "agent_id": agent_id},
            }
            return txn

        try:
            import stripe  # type: ignore[import]
            stripe.api_key = self.api_key
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency="usd",
                metadata={"skill_id": skill_id, "agent_id": agent_id, "proof": proof},
                confirm=True,
                payment_method="pm_card_visa",
            )
            txn = _build_txn(skill_id, agent_id, amount, proof, "stripe")
            txn["stripe"] = intent
            return txn
        except Exception as e:
            return {"status": "error", "error": str(e), "gateway": "stripe"}


class CoinbaseAgentWallet(PaymentGateway):
    """
    Coinbase Agent Wallet stub — crypto-native payments via Coinbase Commerce.
    Set COINBASE_API_KEY env var to enable real charges.
    """

    def __init__(self) -> None:
        self.api_key = os.environ.get("COINBASE_API_KEY")

    def generate_proof(self, skill_id: str, agent_id: str) -> str:
        return _make_proof(skill_id, agent_id)

    def process_payment(self, skill_id: str, agent_id: str, amount: float) -> dict:
        proof = self.generate_proof(skill_id, agent_id)
        charge_id = f"charge_{uuid.uuid4().hex[0:16]}"

        if not self.api_key:
            txn = _build_txn(skill_id, agent_id, amount, proof, "coinbase_stub")
            txn["coinbase"] = {
                "id": charge_id,
                "code": (charge_id[0:8]).upper(),  # type: ignore[no-matching-overload]
                "pricing": {"local": {"amount": str(amount), "currency": "USD"}},
                "timeline": [{"status": "COMPLETED"}],
                "metadata": {"skill_id": skill_id, "agent_id": agent_id},
            }
            return txn

        try:
            import urllib.request, json as _json  # type: ignore[import]
            body = _json.dumps({
                "name": f"Nexus Skill: {skill_id}",
                "pricing_type": "fixed_price",
                "local_price": {"amount": str(amount), "currency": "USD"},
                "metadata": {"skill_id": skill_id, "agent_id": agent_id},
            }).encode()
            headers: dict[str, str] = {
                "X-CC-Api-Key": self.api_key or "",
                "X-CC-Version": "2018-03-22",
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(
                "https://api.commerce.coinbase.com/charges",
                data=body,
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                charge = _json.loads(r.read())
            txn = _build_txn(skill_id, agent_id, amount, proof, "coinbase")
            txn["coinbase"] = charge
            return txn
        except Exception as e:
            return {"status": "error", "error": str(e), "gateway": "coinbase"}


def get_gateway() -> PaymentGateway:
    """Select gateway: PAYMENT_GATEWAY=mock|stripe|coinbase, or auto-detect from env keys."""
    gw = os.environ.get("PAYMENT_GATEWAY", "auto").lower()
    if gw == "stripe":
        return StripePaymentGateway()
    if gw in ("coinbase", "crypto"):
        return CoinbaseAgentWallet()
    if os.environ.get("STRIPE_SECRET_KEY"):
        return StripePaymentGateway()
    if os.environ.get("COINBASE_API_KEY"):
        return CoinbaseAgentWallet()
    return MockPaymentGateway()


def handle_skill_usage(skill_id: str, agent_id: str, action: str = "install") -> dict:
    gateway = get_gateway()
    proof = gateway.generate_proof(skill_id, agent_id)
    log_usage(skill_id, agent_id, action, proof)

    skill = get_skill(skill_id)
    if skill is None:
        return {"status": "error", "message": "Skill not found"}

    price = skill.get("price_per_use") or skill.get("license_fee")
    if price and price > 0:
        return {
            "status": "paid",
            "proof_of_execution": proof,
            "payment": gateway.process_payment(skill_id, agent_id, float(price)),
        }

    return {"status": "free", "proof_of_execution": proof}
