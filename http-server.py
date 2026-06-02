#!/usr/bin/env python3
"""
BoostSuite MCP Server — HTTP Transport (stdlib only)
Exposes BoostSuite tools via HTTP (Streamable HTTP MCP protocol).
Deployed at https://hd-webdesign.si/api/mcp/
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import urllib.request
import urllib.error

BOOSTSUITE_API = os.environ.get("BOOSTSUITE_API", "https://hd-webdesign.si/api/functions")
PORT = int(os.environ.get("MCP_PORT", "8787"))
WALLET = "0xA41A68D6c45d8E39a090648d2a0e602C0abF1275"

TOOLS = [
    {
        "name": "seo_audit",
        "description": "Run a full SEO audit on a website. Returns SEO score (0-100), issues, and fixes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Website URL to audit"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "geo_check",
        "description": "Check AI search visibility (ChatGPT, Gemini, Perplexity).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "business": {"type": "string", "description": "Business name"},
                "location": {"type": "string", "description": "City/region"},
                "niche": {"type": "string", "description": "Industry"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["business", "location", "niche"]
        }
    },
    {
        "name": "ad_copy_generator",
        "description": "Generate ad copy for Google, Facebook, Instagram, LinkedIn, email.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Product/service description"},
                "audience": {"type": "string", "description": "Target audience"},
                "tone": {"type": "string", "description": "Writing tone", "default": "professional"},
                "cta": {"type": "string", "description": "Call to action", "default": "Learn more"},
                "platform": {"type": "string", "description": "google/facebook/instagram/linkedin/email", "default": "google"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["product", "audience"]
        }
    },
    {
        "name": "listing_optimizer",
        "description": "Optimize product/service listings for marketplaces.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "Product/service name"},
                "category": {"type": "string", "description": "Category"},
                "features": {"type": "string", "description": "Key features"},
                "persona": {"type": "string", "description": "Target buyer persona"},
                "platform": {"type": "string", "description": "etsy/amazon/shopify/upwork", "default": "etsy"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["product"]
        }
    },
    {
        "name": "combined_audit",
        "description": "All-in-one website audit: SEO, security, performance, accessibility, GDPR.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Website URL to audit"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "menu_translate",
        "description": "Translate and describe restaurant menu items in 9 languages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "string", "description": "Menu items to translate"},
                "target_language": {"type": "string", "description": "Target language", "default": "English"},
                "tone": {"type": "string", "description": "Style: appetizing/formal/casual/luxury", "default": "appetizing"},
                "api_key": {"type": "string", "description": "BoostSuite API key (optional)"}
            },
            "required": ["items"]
        }
    }
]

ENDPOINT_MAP = {
    "seo_audit": "seo-audit.php",
    "geo_check": "geo-check.php",
    "ad_copy_generator": "ad-copy.php",
    "listing_optimizer": "listing-optimize.php",
    "combined_audit": "combined-audit.php",
    "menu_translate": "translate.php",
}

TOOL_PRICES = {
    "seo_audit": 0.05,
    "geo_check": 0.03,
    "ad_copy_generator": 0.05,
    "listing_optimizer": 0.04,
    "combined_audit": 0.15,
    "menu_translate": 0.02,
}


def build_sse(event_data):
    return f"data: {json.dumps(event_data)}\n\n"


def handle_initialize(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "boostsuite", "version": "1.0.0"}
        }
    }


def handle_tools_list(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": TOOLS}
    }


def check_payment(api_key, tool_name):
    if api_key and api_key.startswith("bs_live_") and len(api_key[8:]) == 24:
        return True, None
    price = TOOL_PRICES.get(tool_name, 0.05)
    return False, {
        "error": "Payment Required",
        "status": 402,
        "x402_version": 1,
        "payment": {
            "network": "base",
            "wallet": WALLET,
            "amount": str(price),
            "currency": "USDC",
            "description": f"BoostSuite {tool_name}",
        },
        "api_key": {
            "freelancer": "EUR19/month - 2,000 calls - https://hd-webdesign.si/boostsuite/",
            "agency": "EUR49/month - unlimited"
        }
    }


def api_post(endpoint, payload):
    url = f"{BOOSTSUITE_API}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def handle_tools_call(request_id, tool_name, arguments):
    if tool_name not in ENDPOINT_MAP:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {tool_name}"})}],
                "isError": True
            }
        }

    api_key = arguments.pop("api_key", None)
    allowed, error = check_payment(api_key, tool_name)
    if not allowed:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(error, indent=2)}],
                "isError": True
            }
        }

    endpoint = ENDPOINT_MAP[tool_name]
    try:
        data = api_post(endpoint, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(data, indent=2, ensure_ascii=False)}]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                "isError": True
            }
        }


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/mcp", "/mcp/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"event: heartbeat\ndata: {}\n\n")
            self.wfile.flush()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/mcp", "/mcp/"):
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_jsonrpc_error(None, -32700, "Parse error")
            return

        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            response = handle_initialize(request_id)
        elif method == "notifications/initialized":
            self.send_response(202)
            self.end_headers()
            return
        elif method == "tools/list":
            response = handle_tools_list(request_id)
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            response = handle_tools_call(request_id, tool_name, arguments)
        elif method == "ping":
            response = {"jsonrpc": "2.0", "id": request_id, "result": {}}
        else:
            self._send_jsonrpc_error(request_id, -32601, f"Method not found: {method}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        sse_data = build_sse(response)
        self.wfile.write(sse_data.encode())
        self.wfile.write(b"event: done\ndata: {}\n\n")
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_jsonrpc_error(self, request_id, code, message):
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        sse_data = build_sse(response)
        self.wfile.write(sse_data.encode())
        self.wfile.write(b"event: done\ndata: {}\n\n")
        self.wfile.flush()


def main():
    server = HTTPServer(("127.0.0.1", PORT), MCPHandler)
    print(f"BoostSuite MCP HTTP Server running on http://127.0.0.1:{PORT}/mcp", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
