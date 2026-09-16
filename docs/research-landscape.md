# Xilinx FPGA agent-tooling landscape

Last reviewed: 2026-09-04. Selection favors a reproducible Linux/Xilinx workflow, explicit safety gates, stable licensing, typed interfaces, and usefulness without attached hardware. Repository commit IDs record the exact revisions inspected; links remain the authoritative upstream source.

## Codex packaging baseline

The layout follows the [official OpenAI plugin guidance](https://learn.chatgpt.com/docs/build-plugins): a plugin is an installable package that may combine Skills and MCP servers, and a local marketplace is the supported development/testing boundary. The checked-in manifest was also validated against the current Codex plugin ingestion schema.

## Agent Skills and workflow collections

| Project | Evidence observed | Decision |
|---|---|---|
| [QingquanYao/xilinx-skill](https://github.com/QingquanYao/xilinx-skill) (`ccffd370`) | Broad Vivado/Vitis HLS/Vitis/PetaLinux coverage, progressive reference library, Codex-compatible Agent Skills layout. README claims MIT, but the inspected revision had no root license file. | Strong workflow reference. Reimplemented concise Codex-native skills here; no source text or assets copied. |
| [Xilinx/ai-assisted-vitis](https://github.com/Xilinx/ai-assisted-vitis) | AMD/Xilinx-maintained examples for knowledge/action agents, Vitis Python API migration, build-log diagnosis, and evidence-driven multi-step workflows. | Used as the preferred mental model for tool-assisted Vitis work. Do not vendor tutorial content. |
| [Nacholazabal/fpga-claude](https://github.com/Nacholazabal/fpga-claude) | MIT CLI/skill for Vivado ILA capture over `hw_server`, CSV export, and protocol analysis. Useful distinction between trigger changes and instrumentation changes. | Incorporated the workflow boundary into `xilinx-hardware-debug`; optional upstream CLI rather than a mandatory dependency. |

## MCP servers

| Project | Evidence observed | Decision |
|---|---|---|
| [mapleleavessssssss-wq/vivado-mcp](https://github.com/mapleleavessssssss-wq/vivado-mcp) (`60b13cf`, PyPI `0.3.25`) | Apache-2.0, Python 3.10+, Linux/Windows, typed curated tools, GUI/Tcl/attach sessions, doctor, report parsing, XDC/IP diagnostics, tests, injection-resistant command transport. | Selected and pinned as the optional full Vivado MCP. |
| [wangyuxin0707/vivado-mcp-agent](https://github.com/wangyuxin0707/vivado-mcp-agent) | MIT, deterministic project/report/AXI/CDC planning and safety gates, but explicitly Windows 11 + Vivado 2025.2 first. | Valuable design reference; not default for this Linux/U250 project. |
| [Xilinx/fpl26_optimization_contest](https://github.com/Xilinx/fpl26_optimization_contest) (`0a580340`, Apache-2.0) | AMD/Xilinx official VivadoMCP and RapidWrightMCP focused on DCP timing analysis, pblocks, fanout/LUT optimization, placement and routing. | Recommended opt-in for post-route physical optimization; too specialized and heavyweight for default loading. |
| [QingquanYao/vitis_mcp](https://github.com/QingquanYao/vitis_mcp) (`ed3c8b80`) | Persistent Vitis Python/XSDB session and broad platform/debug tools. The inspected revision had only three commits and no license file. | Not bundled or auto-installed. Re-evaluate when licensing and maturity are clear. |

The plugin adds its own `fpga-workspace` MCP because repository discovery, XDC auditing, and report extraction should still work on machines with neither Vivado nor Python MCP packages. It deliberately exposes no arbitrary shell/Tcl or write tools.

## RTL, verification, and implementation tools

| Layer | Preferred projects | Why they are routed this way |
|---|---|---|
| Syntax/style/LSP | [CHIPS Alliance Verible](https://github.com/chipsalliance/verible) | Maintained SystemVerilog parser, formatter, style linter and language server. It is a style/syntax layer, not semantic elaboration proof. |
| Fast compile/lint/simulation | [Verilator](https://github.com/verilator/verilator), [Icarus Verilog](https://github.com/steveicarus/iverilog) | Verilator is preferred for synthesizable SV and fast regression; Icarus is a lightweight compatibility option. |
| Python verification | [cocotb](https://github.com/cocotb/cocotb) | Simulator-independent tests and reusable scoreboards; retain simulator-specific CI lanes where behavior differs. |
| Synthesis/formal | [Yosys](https://github.com/YosysHQ/yosys), [SymbiYosys](https://github.com/YosysHQ/sby) | Excellent early structural/formal feedback. Xilinx sign-off remains Vivado because primitives, encrypted IP, timing and implementation models differ. |
| Build orchestration | [FuseSoC](https://github.com/olofk/fusesoc) / [Edalize](https://github.com/olofk/edalize) | Portable core metadata and simulator/backend dispatch; retain existing Make/CMake/Tcl flows instead of forcing migration. |
| Physical design | [Xilinx RapidWright](https://github.com/Xilinx/RapidWright) | Vendor-maintained open-source DCP manipulation and physical optimization for advanced cases. |

## Alveo and host runtime

- [Xilinx/XRT](https://github.com/Xilinx/XRT) is the authoritative open-source runtime/driver surface for Alveo and provides `xrt-smi` plus native host APIs.
- [Xilinx/Vitis_Accel_Examples](https://github.com/Xilinx/Vitis_Accel_Examples) provides maintained host/kernel reference patterns. Copy examples only after matching the installed Vitis/XRT release and target platform.
- [Xilinx/dma_ip_drivers](https://github.com/Xilinx/dma_ip_drivers) is the relevant low-level XDMA/QDMA driver reference. XRT and a platform shell should remain the default when available; custom XDMA is an architectural choice, not a drop-in speed switch.

## AMD documentation baseline

Agent-generated Tcl or constraints must be checked against the installed tool version. The primary document families are [Vivado Tcl scripting (UG894)](https://docs.amd.com/r/en-US/ug894-vivado-tcl-scripting), [XDC and timing constraints (UG903)](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints), [Vivado methodology (UG949)](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology), [synthesis (UG901)](https://docs.amd.com/r/en-US/ug901-vivado-synthesis), [implementation (UG904)](https://docs.amd.com/r/en-US/ug904-vivado-implementation), and [Vitis HLS (UG1399)](https://docs.amd.com/r/en-US/ug1399-vitis-hls). Board files, device data sheets, IP product guides, XRT docs, and release notes override generic examples.

## Exclusions

- No unlicensed repository code is vendored.
- No generic filesystem, SSH, Docker, or unrestricted shell MCP is added; Codex already has scoped local tools and a broad external executor would weaken the safety model.
- No tool is called “sign-off” unless it uses the target Vivado version, target part/platform, actual constraints, and post-route reports.
- No generated pin assignment is treated as authoritative without the exact board schematic/master XDC.
