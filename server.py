#!/usr/bin/env python3
"""
BoostSuite MCP Server
Exposes BoostSuite website audit tools as MCP tools for AI agents.

Tools:
  - seo_audit: Full SEO analysis of a website
  - geo_check: Generative Engine Optimization check (AI search visibility)
  - ad_copy_generator: Generate ad copy for multiple platforms
  - listing_optimizer: Optimize product/service listings
  - combined_audit: All-in-one audit (SEO + Security + Performance + Accessibility + GDPR)
  - menu_translate: Translate/describe menu items (MenuBoost)
"""

import json
import httpx
from mcp.server.fastmcp import FastMCP

BOOSTSUITE_API = "https://hd-webdesign.si/api/functions"

mcp = FastMCP(
    "BoostSuite",
    instructions="Website audit tools for AI agents — SEO, GEO, performance, security, accessibility, GDPR. Powered by BoostSuite (hd-webdesign.si). Call seo_audit with a URL to get a full SEO report, geo_check to check AI search visibility, combined_audit for a comprehensive health check."
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


@mcp.tool()
async def seo_audit(url: str) -> str:
    """Run a full SEO audit on a website. Returns SEO score (0-100), issues found, and actionable recommendations.
    
    Args:
        url: The full website URL to audit (e.g. "https://example.com")
    """
    return await _api_post("seo-audit.php", {"url": url})


@mcp.tool()
async def geo_check(business: str, location: str, niche: str) -> str:
    """Check Generative Engine Optimization (GEO) — how well a business performs in AI-powered search engines like ChatGPT, Gemini, and Perplexity. Returns AI visibility score and optimization tips.
    
    Args:
        business: Business or brand name (e.g. "HD Webdesign")
        location: City or region (e.g. "Ljubljana, Slovenia")
        niche: Industry or category (e.g. "web design agency")
    """
    return await _api_post("geo-check.php", {
        "business": business,
        "location": location,
        "niche": niche
    })


@mcp.tool()
async def ad_copy_generator(product: str, audience: str, tone: str = "professional", cta: str = "Learn more", platform: str = "google") -> str:
    """Generate advertising copy for a product or service. Supports Google Ads, Facebook, Instagram, LinkedIn, and email.
    
    Args:
        product: Product or service name and description
        audience: Target audience (e.g. "restaurant owners in Slovenia")
        tone: Writing tone — "professional", "casual", "urgent", "friendly" (default: "professional")
        cta: Call to action text (default: "Learn more")
        platform: Target platform — "google", "facebook", "instagram", "linkedin", "email" (default: "google")
    """
    return await _api_post("ad-copy.php", {
        "product": product,
        "audience": audience,
        "tone": tone,
        "cta": cta,
        "platform": platform
    })


@mcp.tool()
async def listing_optimizer(product: str, category: str = "", features: str = "", persona: str = "", platform: str = "etsy") -> str:
    """Optimize a product or service listing for better conversions and search visibility.
    
    Args:
        product: Product or service name
        category: Product category (e.g. "SaaS", "restaurant menu", "web design")
        features: Key features or selling points
        persona: Target buyer persona
        platform: Marketplace platform — "etsy", "amazon", "shopify", "upwork", "fiverr" (default: "etsy")
    """
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
async def combined_audit(url: str) -> str:
    """Run a comprehensive all-in-one website audit combining SEO, security, performance, accessibility, and cookie/GDPR checks into a single report. Best for a complete website health check.
    
    Args:
        url: The full website URL to audit (e.g. "https://example.com")
    """
    return await _api_post("combined-audit.php", {"url": url})


@mcp.tool()
async def menu_translate(items: str, target_language: str = "English", tone: str = "appetizing") -> str:
    """Translate and describe restaurant menu items. Creates appetizing multilingual descriptions. Supports 9 languages: Slovenian, English, Croatian, Italian, German, French, Spanish, Turkish, Greek.
    
    Args:
        items: Menu items to translate/describe (e.g. "ćevapčiči - grilled meat sausages" or full menu text)
        target_language: Target language for translation (default: "English")
        tone: Description style — "appetizing", "formal", "casual", "luxury" (default: "appetizing")
    """
    return await _api_post("translate.php", {
        "items": items,
        "target_language": target_language,
        "tone": tone
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
