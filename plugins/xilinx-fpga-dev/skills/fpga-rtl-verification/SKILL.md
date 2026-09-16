---
name: fpga-rtl-verification
description: Verify Verilog, SystemVerilog, or VHDL with lint, elaboration, simulation, assertions, cocotb, formal checks, and CI using open-source or vendor simulators. Use for RTL correctness and regressions; do not treat open-source synthesis or lint as Xilinx implementation sign-off.
---

# FPGA RTL Verification

Build a layered verification argument that can reproduce a failure and distinguish syntax, elaboration, functional, protocol, CDC/reset, and implementation problems.

## Preserve the real compilation model

Inspect existing file lists, source order, language standard, top, include directories, defines, generated sources, vendor libraries and simulator. Prefer the repository's established command. If creating a minimal reproducer, keep it separate and state what it omits.

Choose tools using [references/tool-selection.md](references/tool-selection.md). For protocol, reset and CDC coverage expectations, read [references/verification-plan.md](references/verification-plan.md).

## Layer checks by cost

Start with formatter/style only when requested; never mix a whole-tree format rewrite into a functional fix. Run syntax and semantic lint/elaboration next. Then run focused deterministic tests, followed by the relevant regression. Use assertions and scoreboards for protocol invariants and end-to-end data. Add formal properties where bounded/exhaustive state-space evidence is valuable and assumptions can be reviewed.

For every failure, retain the command, seed, tool/version, top, key parameters and first causal diagnostic. Reduce random failures to a stable seed before changing RTL. A passing test proves only the exercised contract; report known coverage gaps.

## Avoid false confidence

Verible is primarily parsing/style tooling. Icarus supports a smaller SystemVerilog surface. Verilator is excellent for synthesizable-cycle simulation but is not a universal event-driven simulator. Yosys/SymbiYosys support varies by SystemVerilog construct and vendor primitive. Use the target Vivado/XSim or another supported commercial simulator when encrypted Xilinx IP, UNISIM/XPM behavior, SDF, full UVM, or release-specific elaboration matters.
