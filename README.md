# BoostSuite MCP Server

Website audit tools for AI agents — SEO, GEO, performance, security, accessibility, and GDPR compliance.

**Hybrid Payment:** x402 (USDC crypto) for agents + Stripe for human subscribers.

## Tools (6)

| Tool | Description | Cost (x402) |
|------|-------------|-------------|
| `seo_audit` | Full SEO analysis with score and recommendations | 0.05 USDC |
| `geo_check` | AI search visibility check (ChatGPT, Gemini, Perplexity) | 0.03 USDC |
| `ad_copy_generator` | Generate ads for Google, Facebook, Instagram, LinkedIn, email | 0.05 USDC |
| `listing_optimizer` | Optimize product/service listings for marketplaces | 0.04 USDC |
| `combined_audit` | All-in-one comprehensive website audit | 0.15 USDC |
| `menu_translate` | Multilingual menu item descriptions (9 languages) | 0.02 USDC |

## Payment Options

### 1. x402 (USDC) — For AI Agents
- Pay per call, zero protocol fees
- Works on Base network (low gas ~$0.001)
- Agent pays autonomously, no human needed
- [x402.org](https://x402.org)

### 2. API Key — For Human Subscribers
- **Free:** 100 calls/month
- **Freelancer:** €19/month — 2,000 calls
- **Agency:** €49/month — unlimited
- Get your key: https://hd-webdesign.si/boostsuite/

### 3. Free Tier
- 3 calls/day, no key required
- Good for testing and evaluation

## Install

### Via Smithery.ai (recommended)
```bash
npx -y @smithery/cli install @hercegdarko/boostsuite-mcp-server
```

### Manual
```bash
pip install mcp httpx
python server.py
```

## Configuration

Set environment variables:

```bash
# API endpoint (default: hd-webdesign.si)
export BOOSTSUITE_API="https://hd-webdesign.si/api/functions"

# x402 wallet for crypto payments (required for x402)
export X402_WALLET="0xYourUSDCWalletAddress"
export X402_NETWORK="base"
```

## Usage in Claude Desktop / Cursor / Hermes

Add to your MCP config:

```json
{
  "mcpServers": {
    "boostsuite": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "X402_WALLET": "0xYourUSDCWalletAddress"
      }
    }
  }
}
```

## How x402 Works

1. Agent calls a tool (e.g., `seo_audit`)
2. Server responds with `402 Payment Required` + price + wallet address
3. Agent pays USDC to the wallet
4. Agent retries with the transaction hash as proof
5. Server verifies payment and returns the result

```
Agent → "Run SEO audit on example.com"
Server → 402: Pay 0.05 USDC to 0xABC... on Base
Agent → Pays USDC, gets tx hash
Agent → Retries with x402_payment_proof
Server → Returns audit results
```

## Example

Ask your AI agent:
> "Run an SEO audit on https://example.com"

The agent calls `seo_audit(url="https://example.com")` and returns the results.

## API Endpoints

All tools call these BoostSuite PHP endpoints:
- `seo-audit.php` — SEO analysis
- `geo-check.php` — AI visibility check
- `ad-copy.php` — Ad copy generation
- `listing-optimize.php` — Listing optimization
- `combined-audit.php` — All-in-one audit
- `translate.php` — Menu translation

## Powered by

[BoostSuite](https://hd-webdesign.si/boostsuite/) — Website audit toolkit by HD Webdesign
