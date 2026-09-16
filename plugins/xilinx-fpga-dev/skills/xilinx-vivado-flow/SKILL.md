---
name: xilinx-vivado-flow
description: Build, inspect, automate, or debug AMD/Xilinx Vivado RTL projects, Tcl flows, XDC constraints, synthesis, implementation, DRC, timing closure, and bitstream generation. Use for Vivado project and non-project flows; use the Alveo skill for XRT host/kernel architecture and the HLS skill for C/C++ synthesis.
---

# Xilinx Vivado Flow

Deliver a reproducible Vivado change with evidence from the relevant stage, not merely plausible RTL or Tcl.

## Start from project facts

Inspect repository instructions and existing build entry points. Use `fpga_discover_project` and `fpga_check_environment` when available. Establish the installed Vivado version, target part or board/platform, top module, source/file-list ownership, clock/reset plan, constraints, generated-IP policy, and whether the project uses project or non-project mode.

Do not guess a device part, package pin, I/O voltage, board interface, IP version, or generated-output location. Obtain these from the project, board files/schematic, an existing checkpoint, or the user. When they are absent, work on hardware-independent pieces and state what remains unresolved.

## Make the smallest stage-correct change

Preserve the repository's flow. Prefer checked-in Tcl that reconstructs the design over opaque GUI-only state when the project already follows that model. Keep generated files out of source control unless the repository intentionally vendors them. Make batch scripts fail on errors and write reports to deterministic paths.

For the build sequence and evidence gates, read [references/workflow.md](references/workflow.md). For clocks, I/O delays, CDC-related exceptions, and pin constraints, read [references/constraints.md](references/constraints.md).

## Verify at the right abstraction level

Run the fastest relevant checks first: syntax/elaboration, focused simulation, synthesis, then implementation. After synthesis inspect utilization, inferred clocks, CDC, methodology/DRC findings, and unconstrained paths. After implementation inspect post-route timing, DRC, route status and utilization. Preserve the command, tool version, part, report paths, and decisive metrics.

Treat `CRITICAL WARNING` as evidence to classify, not noise to suppress. Treat positive WNS alone as insufficient when paths are unconstrained or asynchronous relationships are wrong.

## State-changing gates

Bitstream generation is a long-running material build step; use the existing project command when requested as part of the task. Programming a physical device, modifying `Vivado_init.tcl`, writing a checkpoint over a baseline, or executing unrestricted Tcl against a live session requires that the user has explicitly put that state change in scope. Resolve the exact target and retain logs before acting.

When the `vivado` MCP exposes only `vivado_mcp_setup_status`, continue with file-level work and use its returned setup command only after explaining the optional dependency to the user.
