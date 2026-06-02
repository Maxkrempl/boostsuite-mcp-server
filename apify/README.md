# BoostSuite MCP Server — Apify Actor

Website audit tools for AI agents — SEO, GEO, performance, security, accessibility, and GDPR compliance.

## Install

```bash
apify create boostsuite-mcp-server -t ts-mcp-proxy
```

Or deploy manually:
```bash
cd boostsuite-apify
npm install
apify push
```

## Usage

### Via Apify MCP Endpoint
```
https://api.apify.com/v2/acts/boostsuite-mcp-server/mcp
```

### Via Apify Client
```javascript
const apifyClient = new ApifyClient({ token: 'YOUR_APIFY_TOKEN' });
const run = await apifyClient.actor('boostsuite-mcp-server').call({
  tool: 'seo_audit',
  arguments: { url: 'https://example.com' }
});
```

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `seo_audit` | Full SEO audit | $0.05 |
| `geo_check` | AI search visibility | $0.03 |
| `ad_copy_generator` | Ad copy generation | $0.05 |
| `listing_optimizer` | Listing optimization | $0.04 |
| `combined_audit` | All-in-one audit | $0.15 |
| `menu_translate` | Menu translation | $0.02 |

## Powered by

[BoostSuite](https://hd-webdesign.si/boostsuite/) — Website audit toolkit by HD Webdesign
