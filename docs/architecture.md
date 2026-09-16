# Plugin architecture

## Loading model

`zcode-plugin-fpga-dev` is a GitHub-hosted ZCode marketplace. Its root `marketplace.json` points to `plugins/xilinx-fpga-dev`, whose `.zcode-plugin/plugin.json` manifest exposes Skills and MCP servers through ZCode-native fields.

```text
ZCode
  +-- skills/
  |     +-- Vivado flow
  |     +-- Vitis HLS
  |     +-- RTL verification
  |     +-- Alveo acceleration
  |     +-- hardware debug
  |     `-- embedded platform
  `-- MCP (namespaced plugin:xilinx-fpga-dev:<server>)
        +-- fpga-workspace (bundled, zero dependency, read-only)
        `-- vivado
              +-- installed vivado-mcp 0.3.25
              `-- setup-status fallback MCP
```

The split is intentional. Skills hold engineering judgment and evidence gates. MCP tools provide deterministic discovery and report extraction. Long-running or state-changing vendor actions stay behind the dedicated Vivado MCP and explicit user authorization.

## Cross-platform Python launcher

ZCode spawns each plugin MCP server via the `command` in `.mcp.json`. There is no interpreter-agnostic template variable, so the repository ships `python3` as the default command — the correct choice on Linux, macOS, and WSL, where ZCode sessions run against a `python3` on PATH.

Windows has no `python3` (the Microsoft Store alias is not usable), so `scripts/setup_windows.py` rewrites the installed copy's `.mcp.json` in place: it prefers the `py` launcher (installed into `C:\Windows` by every python.org install, hence the most reliable), then `python`. It is idempotent, refuses to touch entries with unknown keys, prints exactly what changed, and supports `--command` / `--revert`. Re-run it after a plugin update, because updating restores the shipped file. All other Python sources use only the standard library and are platform-neutral; `fpga_plugin_config.py` even selects per-OS venv layouts (`Scripts\python.exe` vs `bin/python`) and cache roots.

`args` reference scripts through `${ZCODE_PLUGIN_ROOT}`, which ZCode expands for plugin-provided servers; the configuration-file schema is strict (an unknown key drops the server), so the file only uses `type`/`command`/`args`/`timeoutMs`.

## Why the Vivado MCP is optional

Vivado itself is proprietary, large, version-sensitive, and normally installed outside a repository. Automatically downloading Python dependencies during plugin startup would make loading slow and surprising. `run_vivado_mcp.py` therefore searches, in order, an explicitly configured Python interpreter (`ZCODE_FPGA_VIVADO_MCP_PYTHON`), the plugin's isolated cache environment, and a system `vivado-mcp` executable. If none exists, it starts a protocol-compatible setup-status server.

## Update policy

The external MCP version is pinned in `scripts/fpga_plugin_config.py`. Change the pin only after checking the upstream changelog, license, CLI entry point, and no-Vivado test suite. Then run `validate_bundle.py`, reinstall the plugin through ZCode's marketplace flow (and re-run `setup_windows.py` on Windows), and open a new thread.
