#!/usr/bin/env python3
"""Launch the pinned Vivado MCP or a protocol-compatible setup-status server."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from fpga_plugin_config import VIVADO_MCP_VERSION, venv_python


def can_import(python: Path) -> bool:
    try:
        result = subprocess.run(
            [str(python), "-c", "import vivado_mcp"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def main() -> int:
    explicit = os.environ.get("ZCODE_FPGA_VIVADO_MCP_PYTHON") or os.environ.get("CODEX_FPGA_VIVADO_MCP_PYTHON")
    candidates = [Path(explicit).expanduser()] if explicit else []
    candidates.append(venv_python())
    for candidate in candidates:
        if candidate.is_file() and can_import(candidate):
            os.execv(str(candidate), [str(candidate), "-m", "vivado_mcp"])

    executable = shutil.which("vivado-mcp")
    if executable:
        os.execv(executable, [executable, "serve"])

    stub = Path(__file__).resolve().parents[1] / "mcp" / "vivado_setup_stub.py"
    os.environ["ZCODE_FPGA_VIVADO_MCP_EXPECTED"] = VIVADO_MCP_VERSION
    os.execv(sys.executable, [sys.executable, str(stub)])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
