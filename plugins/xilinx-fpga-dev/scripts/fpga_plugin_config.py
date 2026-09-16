"""Shared configuration for the Xilinx FPGA ZCode plugin."""

from __future__ import annotations

import os
from pathlib import Path

VIVADO_MCP_PACKAGE = "vivado-mcp"
VIVADO_MCP_VERSION = "0.3.25"


def _env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def cache_root() -> Path:
    override = _env("ZCODE_FPGA_CACHE_DIR", "CODEX_FPGA_CACHE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        base = Path(local) if local else Path.home() / "AppData" / "Local"
    else:
        xdg = os.environ.get("XDG_CACHE_HOME")
        base = Path(xdg).expanduser() if xdg else Path.home() / ".cache"
    return (base / "zcode-fpga-dev").resolve()


def venv_python() -> Path:
    root = cache_root() / "vivado-mcp-venv"
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
