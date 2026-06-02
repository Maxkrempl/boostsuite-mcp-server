# BoostSuite MCP Server

Website audit tools for AI agents — SEO, GEO, performance, security, accessibility, and GDPR compliance.

## Tools (9)

| Tool | Description |
|------|-------------|
| `seo_audit` | Full SEO analysis with score and recommendations |
| `geo_check` | AI search visibility (ChatGPT, Gemini, Perplexity) |
| `ad_copy_generator` | Generate ads for Google, Facebook, Instagram, LinkedIn, email |
| `listing_optimizer` | Optimize product/service listings |
| `combined_audit` | All-in-one comprehensive audit |
| `accessibility_audit` | WCAG 2.1 compliance check |
| `security_audit` | Security vulnerability scan |
| `cookie_gdpr_audit` | Cookie/GDPR compliance check |
| `performance_audit` | Page speed & Core Web Vitals |

## Install

### Via Smithery.ai (recommended)
```bash
npx -y @smithery/cli install @hercegdarko/boosuite-mcp-server
```

### Via uvx
```bash
uvx boosuite-mcp-server
```

### Manual
```bash
pip install mcp httpx
python server.py
```

## Usage in Claude Desktop / Cursor / Hermes

Add to your MCP config:

```json
{
  "mcpServers": {
    "boosuite": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Or in Hermes `config.yaml`:
```yaml
mcp_servers:
  boostsuite:
    command: "python3"
    args: ["/home/darko/boostsuite-mcp-server/server.py"]
```

## Example

Ask your AI agent:
> "Run an SEO audit on https://example.com"

The agent will call `seo_audit(url="https://example.com")` and return the results.

## Powered by

[BoostSuite](https://hd-webdesign.si/boost-suite/) — Website audit toolkit by HD Webdesign
