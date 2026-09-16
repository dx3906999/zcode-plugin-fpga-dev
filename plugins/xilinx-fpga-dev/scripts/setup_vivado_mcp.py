#!/usr/bin/env python3
"""Install the selected Vivado MCP into an isolated user-cache venv."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import venv
from pathlib import Path

from fpga_plugin_config import VIVADO_MCP_PACKAGE, VIVADO_MCP_VERSION, cache_root, venv_python


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=VIVADO_MCP_VERSION)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Pass --upgrade to pip while retaining the requested version pin.",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[A-Za-z0-9_.+-]*)?", args.version):
        parser.error("--version must be a concrete PEP 440-like version, not a range")

    target = cache_root() / "vivado-mcp-venv"
    requirement = f"{VIVADO_MCP_PACKAGE}=={args.version}"
    plan = {
        "venv": str(target),
        "python": str(venv_python()),
        "requirement": requirement,
        "modifies_vivado_init": False,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    if not venv_python().exists():
        venv.EnvBuilder(with_pip=True, clear=False).create(target)
    command = [str(venv_python()), "-m", "pip", "install"]
    if args.upgrade:
        command.append("--upgrade")
    command.append(requirement)
    subprocess.run(command, check=True)
    check = subprocess.run(
        [str(venv_python()), "-c", "import vivado_mcp; print(vivado_mcp.__version__)"],
        check=True,
        capture_output=True,
        text=True,
    )
    plan["installed_version"] = check.stdout.strip()
    print(json.dumps(plan, indent=2))
    print("Restart ZCode or open a new thread so the vivado MCP server is reloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
