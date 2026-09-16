#!/usr/bin/env python3
"""Validate repository-local invariants without requiring ZCode or Vivado."""

from __future__ import annotations

import json
import os
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
ALLOWED_SERVER_KEYS = {"type", "command", "args", "cwd", "env", "enabled", "timeoutMs"}


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON at {path}: {exc}")


def check_stdio_server(command: list[str], expected_tool: str, env: dict[str, str] | None = None) -> None:
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "bundle-validator", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    completed = subprocess.run(
        command,
        input="".join(json.dumps(item) + "\n" for item in requests),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=PLUGIN,
        env=env,
    )
    if completed.returncode != 0:
        fail(f"MCP process failed: {completed.stderr}")
    responses = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    tools = next((item["result"]["tools"] for item in responses if item.get("id") == 2), [])
    if expected_tool not in {tool["name"] for tool in tools}:
        fail(f"MCP did not expose {expected_tool}")


def main() -> int:
    manifest_path = PLUGIN / ".zcode-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    if manifest.get("name") != PLUGIN.name:
        fail("plugin folder and manifest name differ")
    if manifest.get("skills") != "skills" or manifest.get("mcpServers") != ".mcp.json":
        fail("plugin component paths are missing")

    mcp_config = load_json(PLUGIN / ".mcp.json")
    servers = mcp_config.get("mcpServers", {})
    if set(servers) != {"fpga-workspace", "vivado"}:
        fail("unexpected MCP server set")
    for name, entry in servers.items():
        unknown = set(entry) - ALLOWED_SERVER_KEYS
        if unknown:
            fail(f"server '{name}' has keys ZCode would drop: {sorted(unknown)}")
        if "command" not in entry:
            fail(f"server '{name}' is missing command")
        for arg in entry.get("args", []):
            if "${" in str(arg) and "ZCODE_PLUGIN_ROOT" not in str(arg):
                fail(f"server '{name}' uses an unsupported template variable in {arg}")

    expected_skills = {
        "xilinx-vivado-flow", "xilinx-vitis-hls", "fpga-rtl-verification",
        "xilinx-alveo-acceleration", "xilinx-hardware-debug", "xilinx-embedded-platform",
    }
    actual_skills = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
    if actual_skills != expected_skills:
        fail(f"skill set differs: {sorted(actual_skills)}")
    for skill in sorted(actual_skills):
        skill_file = PLUGIN / "skills" / skill / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        if f"name: {skill}" not in text or not text.startswith("---\n"):
            fail(f"invalid frontmatter in {skill_file}")
        if (skill_file.parent / "agents").exists():
            fail(f"codex-only agents/ dir still present for {skill}")

    for script in sorted((PLUGIN / "scripts").glob("*.py")) + sorted((PLUGIN / "mcp").glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            fail(f"{script} does not compile: {exc}")

    self_path = Path(__file__).resolve()
    all_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in REPO.rglob("*")
        if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts and path.resolve() != self_path
    )
    if "restart Codex" in all_text or "Restart Codex" in all_text:
        fail("stale 'Codex' branding remains in the bundle")
    unfinished_marker = "[" + "TODO:"
    if unfinished_marker in all_text:
        fail("unfinished scaffold placeholder found")

    marketplace = load_json(REPO / "marketplace.json")
    entries = {entry["name"]: entry for entry in marketplace.get("plugins", [])}
    entry = entries.get(PLUGIN.name)
    if not entry or entry.get("source") != f"./{PLUGIN.name}":
        fail("marketplace entry does not resolve to plugin")

    server = PLUGIN / "mcp" / "fpga_workspace_server.py"
    check_stdio_server([sys.executable, str(server)], "fpga_discover_project")
    with tempfile.TemporaryDirectory() as temporary:
        fallback_env = os.environ.copy()
        fallback_env["ZCODE_FPGA_CACHE_DIR"] = temporary
        fallback_env["PATH"] = ""
        check_stdio_server(
            [sys.executable, str(PLUGIN / "scripts" / "run_vivado_mcp.py")],
            "vivado_mcp_setup_status",
            env=fallback_env,
        )
    subprocess.run([sys.executable, str(server), "--self-test"], check=True, timeout=15, cwd=PLUGIN)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(PLUGIN / "tests"), "-v"], check=True, timeout=60, cwd=PLUGIN)
    print(json.dumps({"ok": True, "plugin": PLUGIN.name, "skills": len(actual_skills), "mcp_servers": len(servers)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
