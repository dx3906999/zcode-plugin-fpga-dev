#!/usr/bin/env python3
"""Switch the plugin's MCP interpreter for the current OS.

The bundled .mcp.json uses `python3` so the plugin works out of the box on
Linux/macOS/WSL. On Windows `python3` normally does not exist, so run this
script once after installing the plugin (and again after any plugin update):

    py  plugins/xilinx-fpga-dev/scripts/setup_windows.py

It rewrites the .mcp.json next to this script's plugin copy in place,
preferring the `py` launcher, then `python`. Nothing else is touched.
`--revert` restores the cross-platform `python3` default; `--command X`
forces a specific interpreter (absolute paths allowed).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
MCP_JSON = PLUGIN / ".mcp.json"
DEFAULT_COMMAND = "python3"
ALLOWED_KEYS = {"type", "command", "args", "cwd", "env", "enabled", "timeoutMs"}


def probe(executable: str) -> str | None:
    resolved = shutil.which(executable)
    if not resolved:
        return None
    try:
        completed = subprocess.run(
            [resolved, "--version"], capture_output=True, text=True,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    first = (completed.stdout or completed.stderr).strip().splitlines()
    return first[0][:120] if first else resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", help="force a specific interpreter (absolute path allowed)")
    parser.add_argument("--revert", action="store_true", help=f"restore command to {DEFAULT_COMMAND!r}")
    args = parser.parse_args()

    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})

    if args.revert:
        target, extra_args = DEFAULT_COMMAND, []
        note = "restored cross-platform default"
    elif args.command:
        target, extra_args = args.command, []
        note = f"forced via --command"
        if not Path(target).is_absolute() and not shutil.which(target):
            raise SystemExit(f"interpreter not found on PATH: {target}")
    else:
        for candidate in ("py", "python", "python3"):
            found = shutil.which(candidate)
            if not found:
                continue
            target, extra_args = (candidate, ["-3"]) if candidate == "py" else (candidate, [])
            version = probe(candidate)
            print(f"detected interpreter: {candidate} ({version})")
            break
        else:
            raise SystemExit(
                "no Python interpreter found on PATH. Install Python 3.10+ from python.org "
                "(keeps the `py` launcher on PATH), then re-run this script."
            )
        note = "switched for Windows"

    changed = False
    for name, entry in servers.items():
        unknown = set(entry) - ALLOWED_KEYS
        if unknown:
            raise SystemExit(f"unexpected keys {sorted(unknown)} in server '{name}'; refusing to edit")
        script_args = [item for item in entry.get("args", []) if str(item).endswith(".py")]
        if not script_args:
            raise SystemExit(
                f"server '{name}' has no *.py script arg left in {MCP_JSON}; "
                "restore the shipped .mcp.json from the repository instead of editing blindly"
            )
        if entry.get("command") == target and entry.get("args", [])[: len(extra_args)] == extra_args:
            continue
        entry["command"] = target
        entry["args"] = extra_args + script_args
        changed = True
        print(f"{name}: command -> {target} {' '.join(entry['args'])}".rstrip())

    if changed:
        MCP_JSON.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{note}; wrote {MCP_JSON}")
        print("Restart ZCode (or open a new thread) so the MCP servers reload.")
    else:
        print(f"already configured for {target!r}; nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
