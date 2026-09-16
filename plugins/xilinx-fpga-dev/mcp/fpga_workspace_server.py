#!/usr/bin/env python3
"""Zero-dependency, read-only MCP tools for FPGA repositories and reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SERVER_VERSION = "0.1.0"
MAX_SCAN_FILES = 20_000
MAX_REPORT_BYTES = 20 * 1024 * 1024
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".Xil", "__pycache__", ".pytest_cache",
    "node_modules", ".venv", "venv", "ip_user_files", "sim_cache",
}
EXTENSIONS = {
    ".v": "verilog", ".vh": "verilog-header", ".sv": "systemverilog",
    ".svh": "systemverilog-header", ".vhd": "vhdl", ".vhdl": "vhdl",
    ".xdc": "xdc", ".tcl": "tcl", ".xpr": "vivado-project",
    ".xci": "vivado-ip", ".bd": "vivado-block-design", ".dcp": "checkpoint",
    ".xsa": "hardware-platform", ".bit": "bitstream", ".ltx": "debug-probes",
    ".xclbin": "xclbin", ".xo": "kernel-object", ".cfg": "vitis-config",
    ".c": "c", ".cc": "cpp", ".cpp": "cpp", ".h": "c-header", ".hpp": "cpp-header",
    ".sby": "formal-config", ".core": "fusesoc-core",
}


def _path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"path does not exist: {path}")
    return path


def _walk(root: Path, limit: int = MAX_SCAN_FILES):
    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            count += 1
            if count > limit:
                return
            yield Path(current) / name


def check_environment(arguments: dict[str, Any]) -> dict[str, Any]:
    tools = [
        "vivado", "vitis", "vitis_hls", "v++", "xrt-smi", "xbutil", "xbmgmt",
        "verilator", "verible-verilog-lint", "verible-verilog-format", "iverilog",
        "vvp", "yosys", "sby", "gtkwave", "fusesoc",
    ]
    version_args = {
        "verilator": ["--version"], "iverilog": ["-V"], "yosys": ["-V"],
        "sby": ["--version"], "verible-verilog-lint": ["--version"],
        "fusesoc": ["--version"],
    }
    detected: dict[str, Any] = {}
    probe_versions = bool(arguments.get("probe_versions", True))
    for name in tools:
        executable = shutil.which(name)
        entry: dict[str, Any] = {"available": executable is not None, "path": executable}
        if executable and probe_versions and name in version_args:
            try:
                completed = subprocess.run(
                    [executable, *version_args[name]], capture_output=True, text=True,
                    timeout=5, check=False,
                )
                lines = (completed.stdout + "\n" + completed.stderr).strip().splitlines()
                entry["version"] = lines[0][:300] if lines else "unknown"
            except (OSError, subprocess.TimeoutExpired) as exc:
                entry["version_error"] = type(exc).__name__
        detected[name] = entry
    env_keys = [
        "VIVADO_PATH", "VITIS_PATH", "XILINX_VIVADO", "XILINX_VITIS",
        "XILINX_XRT", "PLATFORM_REPO_PATHS", "XILINX_LOCAL_USER_DATA",
    ]
    return {
        "read_only": True,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "tools": detected,
        "environment": {key: os.environ.get(key) for key in env_keys if os.environ.get(key)},
    }


def discover_project(arguments: dict[str, Any]) -> dict[str, Any]:
    root = _path(str(arguments.get("root", ".")))
    if not root.is_dir():
        raise ValueError("root must be a directory")
    requested_limit = int(arguments.get("max_files", MAX_SCAN_FILES))
    limit = min(max(requested_limit, 1), MAX_SCAN_FILES)
    counts: Counter[str] = Counter()
    important: dict[str, list[str]] = {}
    total = 0
    for file in _walk(root, limit):
        total += 1
        kind = EXTENSIONS.get(file.suffix.lower())
        if kind:
            counts[kind] += 1
            bucket = important.setdefault(kind, [])
            if len(bucket) < 25:
                bucket.append(str(file.relative_to(root)))
        elif file.name in {"Makefile", "CMakeLists.txt", "pyproject.toml", "Dockerfile"}:
            counts["build-metadata"] += 1
            important.setdefault("build-metadata", []).append(str(file.relative_to(root)))
    likely_flows = []
    if counts["vivado-project"] or counts["xdc"]:
        likely_flows.append("vivado")
    if counts["xclbin"] or counts["kernel-object"] or counts["vitis-config"]:
        likely_flows.append("vitis-acceleration")
    if counts["c"] or counts["cpp"]:
        likely_flows.append("hls-or-host-software")
    if counts["formal-config"]:
        likely_flows.append("formal")
    if counts["fusesoc-core"]:
        likely_flows.append("fusesoc")
    return {
        "root": str(root), "read_only": True, "files_examined": total,
        "truncated": total >= limit, "kind_counts": dict(counts),
        "representative_files": important, "likely_flows": likely_flows,
    }


def analyze_xdc(arguments: dict[str, Any]) -> dict[str, Any]:
    path = _path(str(arguments["path"]))
    if not path.is_file() or path.suffix.lower() != ".xdc":
        raise ValueError("path must be an existing .xdc file")
    if path.stat().st_size > MAX_REPORT_BYTES:
        raise ValueError("XDC file exceeds 20 MiB limit")
    text = path.read_text(encoding="utf-8", errors="replace")
    active = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    clocks = []
    pins: dict[str, str] = {}
    io_standards: dict[str, str] = {}
    diagnostics = []
    for number, line in enumerate(active, 1):
        if "create_clock" in line:
            period = re.search(r"-period\s+([0-9.]+)", line)
            name = re.search(r"-name\s+([^\s\]]+)", line)
            clocks.append({"name": name.group(1) if name else None, "period_ns": float(period.group(1)) if period else None, "command": line})
            if not period:
                diagnostics.append({"severity": "warning", "message": "create_clock has no explicit -period", "line": line})
        pin = re.search(r"set_property\s+PACKAGE_PIN\s+(\S+)\s+\[get_ports\s+\{?([^}\]]+)", line)
        if pin:
            pins[pin.group(2).strip()] = pin.group(1)
        ios = re.search(r"set_property\s+IOSTANDARD\s+(\S+)\s+\[get_ports\s+\{?([^}\]]+)", line)
        if ios:
            io_standards[ios.group(2).strip()] = ios.group(1)
        if "set_false_path" in line and "-from" not in line and "-to" not in line and "-through" not in line:
            diagnostics.append({"severity": "warning", "message": "unscoped set_false_path deserves manual review", "line": line})
    missing_iostandard = sorted(set(pins) - set(io_standards))
    if missing_iostandard:
        diagnostics.append({"severity": "warning", "message": "ports have PACKAGE_PIN but no directly matched IOSTANDARD", "ports": missing_iostandard})
    return {
        "path": str(path), "read_only": True, "active_commands": len(active),
        "clocks": clocks, "package_pins": pins, "io_standards": io_standards,
        "clock_groups": sum("set_clock_groups" in line for line in active),
        "false_paths": sum("set_false_path" in line for line in active),
        "input_delays": sum("set_input_delay" in line for line in active),
        "output_delays": sum("set_output_delay" in line for line in active),
        "diagnostics": diagnostics,
        "limitations": [
            "Static regex analysis does not expand Tcl variables, loops, sourced files, or get_* queries.",
            "Pin validity requires the exact part, board schematic/master XDC, and Vivado DRC.",
        ],
    }


def parse_vivado_report(arguments: dict[str, Any]) -> dict[str, Any]:
    path = _path(str(arguments["path"]))
    if not path.is_file():
        raise ValueError("path must be a report file")
    if path.stat().st_size > MAX_REPORT_BYTES:
        raise ValueError("report exceeds 20 MiB limit")
    text = path.read_text(encoding="utf-8", errors="replace")
    metrics: dict[str, Any] = {}
    patterns = {
        "wns_ns": r"\bWNS(?:\(ns\))?\s*[:|]?\s*(-?\d+(?:\.\d+)?)",
        "tns_ns": r"\bTNS(?:\(ns\))?\s*[:|]?\s*(-?\d+(?:\.\d+)?)",
        "whs_ns": r"\bWHS(?:\(ns\))?\s*[:|]?\s*(-?\d+(?:\.\d+)?)",
        "ths_ns": r"\bTHS(?:\(ns\))?\s*[:|]?\s*(-?\d+(?:\.\d+)?)",
        "failing_endpoints": r"\bFailing Endpoints\s*[:|]?\s*(\d+)",
        "total_endpoints": r"\bTotal Endpoints\s*[:|]?\s*(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metrics[key] = float(match.group(1)) if "." in match.group(1) else int(match.group(1))
    # Vivado timing summaries commonly put metric names in one row and values
    # in a later row after a dashed separator rather than using "WNS: value".
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "WNS(ns)" not in line or "TNS(ns)" not in line:
            continue
        headers = re.findall(r"WNS\(ns\)|TNS\(ns\)|Failing Endpoints|Total Endpoints|WHS\(ns\)|THS\(ns\)", line, re.IGNORECASE)
        for candidate in lines[index + 1:index + 5]:
            values = re.findall(r"-?\d+(?:\.\d+)?", candidate.replace(",", ""))
            if len(values) < len(headers) or set(candidate.strip()) <= {"-", " ", "|"}:
                continue
            mapped = dict(zip(headers, values))
            key_map = {
                "wns(ns)": "wns_ns", "tns(ns)": "tns_ns", "whs(ns)": "whs_ns",
                "ths(ns)": "ths_ns", "failing endpoints": "failing_endpoints",
                "total endpoints": "total_endpoints",
            }
            for header, value in mapped.items():
                key = key_map[header.lower()]
                metrics.setdefault(key, float(value) if "." in value else int(value))
            break
        break
    table_metrics = {}
    for label in ["Slice LUTs", "CLB LUTs", "Slice Registers", "CLB Registers", "Block RAM Tile", "DSPs", "URAM"]:
        match = re.search(rf"^\s*\|?\s*{re.escape(label)}\s*\|\s*([0-9,]+)", text, re.MULTILINE | re.IGNORECASE)
        if match:
            table_metrics[label] = int(match.group(1).replace(",", ""))
    warning_lines = []
    for line in text.splitlines():
        if re.search(r"CRITICAL WARNING|ERROR:|VIOLATED", line, re.IGNORECASE):
            warning_lines.append(line.strip()[:800])
            if len(warning_lines) >= 100:
                break
    timing_met = None
    if "wns_ns" in metrics:
        timing_met = metrics["wns_ns"] >= 0 and metrics.get("whs_ns", 0) >= 0
    return {
        "path": str(path), "read_only": True, "metrics": metrics,
        "utilization_used": table_metrics, "timing_met_inferred": timing_met,
        "diagnostic_excerpt": warning_lines,
        "limitations": "Use the original report and target-tool run for sign-off; this parser extracts common text layouts only.",
    }


TOOLS = {
    "fpga_check_environment": (
        "Detect AMD/Xilinx and open-source FPGA tools. Only short, safe version probes are executed; Vivado/Vitis builds are never started.",
        {"type": "object", "properties": {"probe_versions": {"type": "boolean", "default": True}}, "additionalProperties": False},
        check_environment,
    ),
    "fpga_discover_project": (
        "Read-only inventory of RTL, XDC, Vivado, HLS, Alveo, formal, and build files under a project root.",
        {"type": "object", "properties": {"root": {"type": "string"}, "max_files": {"type": "integer", "minimum": 1, "maximum": MAX_SCAN_FILES}}, "required": ["root"], "additionalProperties": False},
        discover_project,
    ),
    "fpga_analyze_xdc": (
        "Conservative static summary of clocks, pins, I/O standards, delays, exceptions, and obvious XDC review risks.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False},
        analyze_xdc,
    ),
    "fpga_parse_vivado_report": (
        "Extract common timing, utilization, violation, critical-warning, and error evidence from a Vivado text report.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False},
        parse_vivado_report,
    ),
}


def tool_list() -> dict[str, Any]:
    return {"tools": [{"name": name, "description": desc, "inputSchema": schema} for name, (desc, schema, _) in TOOLS.items()]}


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def serve() -> int:
    for raw in sys.stdin:
        request: dict[str, Any] | None = None
        try:
            request = json.loads(raw)
            method = request.get("method")
            request_id = request.get("id")
            if method == "initialize":
                protocol = request.get("params", {}).get("protocolVersion", "2024-11-05")
                result = {"protocolVersion": protocol, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "fpga-workspace", "version": SERVER_VERSION}}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = tool_list()
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                if name not in TOOLS:
                    raise ValueError(f"unknown tool: {name}")
                data = TOOLS[name][2](params.get("arguments") or {})
                result = {"content": [{"type": "text", "text": json.dumps(data, indent=2, ensure_ascii=False)}], "structuredContent": data}
            elif method and method.startswith("notifications/"):
                continue
            else:
                if request_id is not None:
                    send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}})
                continue
            if request_id is not None:
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
        except Exception as exc:
            request_id = request.get("id") if request else None
            if request_id is not None:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": str(exc)}})
    return 0


def self_test() -> int:
    listed = tool_list()["tools"]
    assert len(listed) == 4
    assert all(tool["name"].startswith("fpga_") for tool in listed)
    env = check_environment({"probe_versions": False})
    assert env["read_only"] is True
    print(json.dumps({"ok": True, "server": "fpga-workspace", "tools": len(listed)}))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    raise SystemExit(self_test() if args.self_test else serve())
