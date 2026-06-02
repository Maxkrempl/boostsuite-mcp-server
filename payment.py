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
X402_WALLET = os.environ.get("X402_WALLET", "0xA41A68D6c45d8E39a090648d2a0e602C0abF1275")  # USDC receiving wallet address
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
    
    Flow:
    1. Agent calls tool → gets 402 Payment Required with price + wallet
    2. Agent pays USDC to wallet on Base network
    3. Agent retries with tx hash as payment_proof
    4. We verify the tx on Base blockchain
    """
    import httpx as _httpx

    if tool_name not in X402_PRICES:
        return PaymentResult(False, "x402", f"Unknown tool: {tool_name}")

    price = X402_PRICES[tool_name]

    if not payment_proof:
        return PaymentResult(
            False, "x402",
            f"Payment required: {price} USDC to {X402_WALLET} on {X402_NETWORK}"
        )

    # Verify on-chain via Base blockchain explorer (Blockscout API — free, no key)
    try:
        url = f"https://base.blockscout.com/api/v2/transactions/{payment_proof}"
        resp = _httpx.get(url, timeout=10)
        if resp.status_code != 200:
            return PaymentResult(False, "x402", f"Transaction not found: {payment_proof}")

        tx = resp.json()

        # Check if transaction is successful
        if tx.get("status") != "ok":
            return PaymentResult(False, "x402", "Transaction failed or pending")

        # Check recipient matches our wallet
        to_addr = (tx.get("to") or {}).get("hash", "").lower()
        if to_addr != X402_WALLET.lower():
            return PaymentResult(False, "x402", f"Wrong recipient: {to_addr}")

        # Check value (USDC has 6 decimals)
        value = int(tx.get("value", "0"))
        expected = int(price * 10**6)
        if value < expected:
            return PaymentResult(False, "x402", f"Insufficient: got {value/10**6} USDC, need {price}")

        return PaymentResult(True, "x402", f"Verified: {price} USDC (tx: {payment_proof[:16]}...)")

    except Exception as e:
        return PaymentResult(False, "x402", f"Verification error: {str(e)}")


def check_payment(tool_name: str, api_key: Optional[str] = None,
                  x402_proof: Optional[str] = None) -> PaymentResult:
    """
    Check payment for a tool call. NO free tier for API/MCP.
    Tries methods in order:
    1. API key (if provided)
    2. x402 payment (if proof provided)
    3. Otherwise → Payment Required
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

    # No free API calls — must pay or use key
    return PaymentResult(False, "payment_required", "API access requires payment or API key")


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
