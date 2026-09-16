#!/usr/bin/env python3
"""Minimal MCP server used when the optional vivado-mcp package is absent."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def send(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main() -> int:
    setup = Path(__file__).resolve().parents[1] / "scripts" / "setup_vivado_mcp.py"
    for raw in sys.stdin:
        try:
            request = json.loads(raw)
            method = request.get("method")
            request_id = request.get("id")
            if method == "initialize":
                version = request.get("params", {}).get("protocolVersion", "2024-11-05")
                result = {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "vivado-setup-status", "version": "0.1.0"},
                }
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": "vivado_mcp_setup_status",
                            "description": "Explain why Vivado automation tools are unavailable and show the explicit setup command. This tool does not install anything.",
                            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
                        }
                    ]
                }
            elif method == "tools/call":
                if request.get("params", {}).get("name") != "vivado_mcp_setup_status":
                    raise ValueError("unknown tool")
                expected = os.environ.get(
                    "ZCODE_FPGA_VIVADO_MCP_EXPECTED",
                    os.environ.get("CODEX_FPGA_VIVADO_MCP_EXPECTED", "0.3.25"),
                )
                data = {
                    "available": False,
                    "expected_version": expected,
                    "setup_command": f"{sys.executable} {setup}",
                    "note": "Run setup explicitly, then restart ZCode. Setup creates a cache venv and does not modify Vivado_init.tcl.",
                }
                result = {
                    "content": [{"type": "text", "text": json.dumps(data, indent=2)}],
                    "structuredContent": data,
                }
            elif method and method.startswith("notifications/"):
                continue
            else:
                if request_id is not None:
                    send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}})
                continue
            if request_id is not None:
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
        except Exception as exc:  # keep the stdio server alive on malformed input
            request_id = request.get("id") if isinstance(locals().get("request"), dict) else None
            if request_id is not None:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc)}})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
