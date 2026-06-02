#!/usr/bin/env python3
"""
BoostSuite MCP Server
Exposes BoostSuite website audit tools as MCP tools for AI agents.

Hybrid Payment:
  - x402 (USDC) for AI agents — microtransactions, zero fees
  - API keys for human subscribers — Stripe-backed plans

Tools:
  - seo_audit: Full SEO analysis of a website
  - geo_check: Generative Engine Optimization check (AI search visibility)
  - ad_copy_generator: Generate ad copy for multiple platforms
  - listing_optimizer: Optimize product/service listings
  - combined_audit: All-in-one audit (SEO + Security + Performance + Accessibility + GDPR)
  - menu_translate: Translate/describe menu items (MenuBoost)
"""

import json
import os
import httpx
from mcp.server.fastmcp import FastMCP
from payment import (
    check_payment, get_payment_required_response,
    X402_PRICES, PaymentError
)

BOOSTSUITE_API = os.environ.get("BOOSTSUITE_API", "https://hd-webdesign.si/api/functions")
X402_WALLET = os.environ.get("X402_WALLET", "")

mcp = FastMCP(
    "BoostSuite",
    instructions="""BoostSuite — Website audit tools for AI agents.

Payment options:
1. x402 (USDC) — Pay per call, zero fees. Example: 0.05 USDC for SEO audit.
2. API Key — Subscribe at https://hd-webdesign.si/boostsuite for monthly plans.
3. Free — 3 calls/day (no key needed).

To pay with x402: When you get a 402 response, pay the USDC amount to the wallet address shown, then retry with the transaction hash.

Tools: seo_audit, geo_check, ad_copy_generator, listing_optimizer, combined_audit, menu_translate."""
)


async def _api_post(endpoint: str, payload: dict) -> str:
    """Call a BoostSuite PHP API endpoint."""
    url = f"{BOOSTSUITE_API}/{endpoint}"
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(url, json=payload)
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"error": "Request timed out after 60s"})
        except Exception as e:
            return json.dumps({"error": str(e)})


def _check_payment_or_error(tool_name: str, api_key: str = None) -> str | None:
    """
    Check payment for a tool. Returns error JSON if payment required, None if OK.
    """
    result = check_payment(tool_name, api_key=api_key)

    if result.success:
        return None  # Payment OK

    # Payment required — return 402 response
    response = get_payment_required_response(tool_name)
    return json.dumps(response, indent=2)


@mcp.tool()
async def seo_audit(url: str, api_key: str = None) -> str:
    """Run a full SEO audit on a website. Returns SEO score (0-100), issues found, and actionable recommendations.

    Cost: 0.05 USDC (x402) or free with API key.

    Args:
        url: The full website URL to audit (e.g. "https://example.com")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("seo_audit", api_key)
    if payment_error:
        return payment_error
    return await _api_post("seo-audit.php", {"url": url})


@mcp.tool()
async def geo_check(business: str, location: str, niche: str, api_key: str = None) -> str:
    """Check Generative Engine Optimization (GEO) — how well a business performs in AI-powered search engines like ChatGPT, Gemini, and Perplexity. Returns AI visibility score and optimization tips.

    Cost: 0.03 USDC (x402) or free with API key.

    Args:
        business: Business or brand name (e.g. "HD Webdesign")
        location: City or region (e.g. "Ljubljana, Slovenia")
        niche: Industry or category (e.g. "web design agency")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("geo_check", api_key)
    if payment_error:
        return payment_error
    return await _api_post("geo-check.php", {
        "business": business,
        "location": location,
        "niche": niche
    })


@mcp.tool()
async def ad_copy_generator(product: str, audience: str, tone: str = "professional", cta: str = "Learn more", platform: str = "google", api_key: str = None) -> str:
    """Generate advertising copy for a product or service. Supports Google Ads, Facebook, Instagram, LinkedIn, and email.

    Cost: 0.05 USDC (x402) or free with API key.

    Args:
        product: Product or service name and description
        audience: Target audience (e.g. "restaurant owners in Slovenia")
        tone: Writing tone — "professional", "casual", "urgent", "friendly" (default: "professional")
        cta: Call to action text (default: "Learn more")
        platform: Target platform — "google", "facebook", "instagram", "linkedin", "email" (default: "google")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("ad_copy_generator", api_key)
    if payment_error:
        return payment_error
    return await _api_post("ad-copy.php", {
        "product": product,
        "audience": audience,
        "tone": tone,
        "cta": cta,
        "platform": platform
    })


@mcp.tool()
async def listing_optimizer(product: str, category: str = "", features: str = "", persona: str = "", platform: str = "etsy", api_key: str = None) -> str:
    """Optimize a product or service listing for better conversions and search visibility.

    Cost: 0.04 USDC (x402) or free with API key.

    Args:
        product: Product or service name
        category: Product category (e.g. "SaaS", "restaurant menu", "web design")
        features: Key features or selling points
        persona: Target buyer persona
        platform: Marketplace platform — "etsy", "amazon", "shopify", "upwork", "fiverr" (default: "etsy")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("listing_optimizer", api_key)
    if payment_error:
        return payment_error
    payload = {"product": product}
    if category:
        payload["category"] = category
    if features:
        payload["features"] = features
    if persona:
        payload["persona"] = persona
    if platform:
        payload["platform"] = platform
    return await _api_post("listing-optimize.php", payload)


@mcp.tool()
async def combined_audit(url: str, api_key: str = None) -> str:
    """Run a comprehensive all-in-one website audit combining SEO, security, performance, accessibility, and cookie/GDPR checks into a single report. Best for a complete website health check.

    Cost: 0.15 USDC (x402) or free with API key.

    Args:
        url: The full website URL to audit (e.g. "https://example.com")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("combined_audit", api_key)
    if payment_error:
        return payment_error
    return await _api_post("combined-audit.php", {"url": url})


@mcp.tool()
async def menu_translate(items: str, target_language: str = "English", tone: str = "appetizing", api_key: str = None) -> str:
    """Translate and describe restaurant menu items. Creates appetizing multilingual descriptions. Supports 9 languages: Slovenian, English, Croatian, Italian, German, French, Spanish, Turkish, Greek.

    Cost: 0.02 USDC (x402) or free with API key.

    Args:
        items: Menu items to translate/describe (e.g. "ćevapčiči - grilled meat sausages" or full menu text)
        target_language: Target language for translation (default: "English")
        tone: Description style — "appetizing", "formal", "casual", "luxury" (default: "appetizing")
        api_key: Optional BoostSuite API key for paid access
    """
    payment_error = _check_payment_or_error("menu_translate", api_key)
    if payment_error:
        return payment_error
    return await _api_post("translate.php", {
        "items": items,
        "target_language": target_language,
        "tone": tone
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
