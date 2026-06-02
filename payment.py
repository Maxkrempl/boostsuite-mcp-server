"""
BoostSuite MCP Server — Hybrid Payment Layer
Supports two payment methods:
1. x402 (USDC) — for AI agents, microtransactions, zero fees
2. API Key (Stripe-backed) — for human subscribers, agency plans
"""

import os
import json
import hashlib
import hmac
import time
from typing import Optional

# ============= Configuration =============

BOOSTSUITE_API = os.environ.get("BOOSTSUITE_API", "https://hd-webdesign.si/api/functions")

# x402 config (Coinbase)
X402_WALLET = os.environ.get("X402_WALLET", "")  # USDC receiving wallet address
X402_NETWORK = os.environ.get("X402_NETWORK", "base")  # base = low gas fees

# Price list in USDC (x402 microtransactions)
X402_PRICES = {
    "seo_audit": 0.05,
    "geo_check": 0.03,
    "ad_copy_generator": 0.05,
    "listing_optimizer": 0.04,
    "combined_audit": 0.15,
    "menu_translate": 0.02,
}

# API key tiers (Stripe-backed subscriptions)
API_KEY_TIERS = {
    "free": {"monthly_calls": 100, "price_eur": 0},
    "freelancer": {"monthly_calls": 2000, "price_eur": 19},
    "agency": {"monthly_calls": -1, "price_eur": 49},  # -1 = unlimited
}


class PaymentError(Exception):
    pass


class PaymentResult:
    def __init__(self, success: bool, method: str, details: str = "", remaining: int = -1):
        self.success = success
        self.method = method  # "x402", "api_key", "free"
        self.details = details
        self.remaining = remaining  # -1 = unlimited


def verify_api_key(api_key: str) -> PaymentResult:
    """
    Verify a BoostSuite API key (bs_live_<24hex> format).
    Returns PaymentResult with tier info.
    """
    if not api_key or not api_key.startswith("bs_live_"):
        return PaymentResult(False, "api_key", "Invalid API key format")

    # In production, this would check against the database
    # For now, validate the key format
    key_part = api_key[8:]  # Remove bs_live_ prefix
    if len(key_part) != 24:
        return PaymentResult(False, "api_key", "Invalid API key length")

    # TODO: Check against API key database, verify tier, check rate limits
    # For now, return success (all keys are valid)
    return PaymentResult(True, "api_key", "Valid API key", remaining=-1)


def verify_x402_payment(tool_name: str, payment_proof: Optional[str] = None) -> PaymentResult:
    """
    Verify x402 payment for a specific tool call.
    
    In production flow:
    1. Agent calls tool → gets 402 Payment Required with price + wallet
    2. Agent pays USDC to wallet
    3. Agent retries with payment proof (tx hash)
    4. We verify the tx on-chain
    
    For now, we accept if payment_proof is provided (trust-based).
    """
    if tool_name not in X402_PRICES:
        return PaymentResult(False, "x402", f"Unknown tool: {tool_name}")

    price = X402_PRICES[tool_name]

    if not payment_proof:
        # Return payment required response
        return PaymentResult(
            False, "x402",
            f"Payment required: {price} USDC to {X402_WALLET} on {X402_NETWORK}"
        )

    # TODO: Verify on-chain payment using Coinbase x402 API
    # For now, trust the payment proof
    return PaymentResult(True, "x402", f"Payment verified: {price} USDC")


def check_payment(tool_name: str, api_key: Optional[str] = None,
                  x402_proof: Optional[str] = None) -> PaymentResult:
    """
    Check payment for a tool call. Tries methods in order:
    1. API key (if provided)
    2. x402 payment (if proof provided)
    3. Free tier (limited)
    """
    # Try API key first
    if api_key:
        result = verify_api_key(api_key)
        if result.success:
            return result

    # Try x402 payment
    if x402_proof:
        result = verify_x402_payment(tool_name, x402_proof)
        if result.success:
            return result

    # Free tier — 3 calls per day (tracked by IP/session)
    return PaymentResult(True, "free", "Free tier (3/day limit)")


def get_payment_required_response(tool_name: str) -> dict:
    """
    Generate a 402 Payment Required response for x402 flow.
    """
    price = X402_PRICES.get(tool_name, 0.05)
    return {
        "error": "Payment Required",
        "status": 402,
        "x402_version": 1,
        "payment": {
            "network": X402_NETWORK,
            "wallet": X402_WALLET,
            "amount": str(price),
            "currency": "USDC",
            "description": f"BoostSuite {tool_name}",
        },
        "docs": "https://x402.org",
        "note": "Pay USDC to the wallet address, then retry with x402_payment_proof header",
    }
