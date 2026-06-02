# BoostSuite MCP Server

Website audit tools for AI agents — SEO, GEO, performance, security, accessibility, and GDPR compliance.

**Hybrid Payment:** x402 (USDC crypto) for agents + Stripe for human subscribers.

## Live Server

**MCP Endpoint:** `https://hd-webdesign.si/api/mcp/`

No installation needed — agents can connect directly via HTTP.

## Tools (6)

| Tool | Description | Cost (x402) |
|------|-------------|-------------|
| `seo_audit` | Full SEO analysis with score and recommendations | 0.05 USDC |
| `geo_check` | AI search visibility check (ChatGPT, Gemini, Perplexity) | 0.03 USDC |
| `ad_copy_generator` | Generate ads for Google, Facebook, Instagram, LinkedIn, email | 0.05 USDC |
| `listing_optimizer` | Optimize product/service listings for marketplaces | 0.04 USDC |
| `combined_audit` | All-in-one comprehensive website audit | 0.15 USDC |
| `menu_translate` | Multilingual menu item descriptions (9 languages) | 0.02 USDC |

## Quick Start

### Remote (recommended)
Point your MCP client to our hosted server:

```json
{
  "mcpServers": {
    "boostsuite": {
      "url": "https://hd-webdesign.si/api/mcp/"
    }
  }
}
```

### Local Install
```bash
git clone https://github.com/Maxkrempl/boostsuite-mcp-server.git
cd boostsuite-mcp-server
python3 http-server.py
```

Then configure your MCP client:
```json
{
  "mcpServers": {
    "boostsuite": {
      "url": "http://localhost:8787/mcp"
    }
  }
}
```

## Payment

### No free API calls
All API/MCP calls require payment. Browser visitors get 1 free audit on the web UI.

### Option 1: x402 (USDC) — For AI Agents
1. Call a tool → get `402 Payment Required` with price + wallet
2. Pay USDC to the wallet on Base network
3. Retry with tx hash in `X-Payment-Proof` header

**Wallet:** `0xA41A68D6c45d8E39a090648d2a0e602C0abF1275` (Base)

**Prices:**
- SEO audit: 0.05 USDC
- GEO check: 0.03 USDC
- Ad copy: 0.05 USDC
- Listing optimize: 0.04 USDC
- Combined audit: 0.15 USDC
- Menu translate: 0.02 USDC

### Option 2: API Key — For Human Subscribers
Subscribe at https://hd-webdesign.si/boostsuite/ and pass your key:

```json
{
  "arguments": {
    "url": "https://example.com",
    "api_key": "bs_live_your_key_here"
  }
}
```

| Plan | Price | Calls/month |
|------|-------|-------------|
| Freelancer | €19/mo | 2,000 |
| Agency | €49/mo | Unlimited |

## Testing

```bash
# List tools
curl -X POST https://hd-webdesign.si/api/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Run SEO audit (will return 402 without payment)
curl -X POST https://hd-webdesign.si/api/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"seo_audit","arguments":{"url":"https://example.com"}}}'
```

## Architecture

```
Agent → https://hd-webdesign.si/api/mcp/ (PHP proxy)
       → http://127.0.0.1:8787/mcp (Python MCP server)
       → https://hd-webdesign.si/api/functions/*.php (BoostSuite API)
```

- **PHP proxy** (`api/mcp/index.php`) — routes requests to local MCP server
- **Python MCP server** (`http-server.py`) — handles MCP protocol, payment checks
- **BoostSuite API** (`api/functions/`) — actual audit/analysis logic

## API Endpoints

| Endpoint | Tool | Auth |
|----------|------|------|
| `seo-audit.php` | SEO audit | Required |
| `geo-check.php` | GEO check | Required |
| `ad-copy.php` | Ad copy | Required |
| `listing-optimize.php` | Listing optimize | Required |
| `combined-audit.php` | Combined audit | 1 free/browser, then required |
| `translate.php` | Menu translate | Required |

## Powered by

[BoostSuite](https://hd-webdesign.si/boostsuite/) — Website audit toolkit by HD Webdesign
