---
name: xilinx-vitis-hls
description: Develop or optimize AMD/Xilinx Vitis HLS C/C++ kernels and IP, including interface synthesis, pragmas/directives, loop II, latency, memory architecture, dataflow, C simulation, synthesis reports, and RTL co-simulation. Do not use for ordinary host software or hand-written RTL-only work.
---

# Xilinx Vitis HLS

Turn an algorithm into a measured hardware microarchitecture while keeping a software golden model.

## Establish the contract

Inspect the top function, types, testbench, target part/platform, clock and uncertainty, interface protocol, transaction sizes, throughput/latency target, numerical tolerance, memory layout and reset/control requirements. Preserve bit-accurate behavior. Do not replace types, reorder floating-point operations, or add pragmas until the reference tests and acceptance metric are clear.

Use [references/optimization.md](references/optimization.md) for the evidence-driven optimization loop and [references/interfaces.md](references/interfaces.md) for AXI and host-integration decisions.

## Work in measured iterations

Keep synthesizable kernel code separate from the testbench. Run C simulation before synthesis. Change one coherent architectural hypothesis at a time, then record latency, achieved II, clock estimate, LUT/FF/BRAM/URAM/DSP usage and the limiting dependency or port. Use report evidence rather than assuming `PIPELINE`, `UNROLL`, `ARRAY_PARTITION`, or `DATAFLOW` helps.

When correctness is established, run C/RTL co-simulation with the representative boundary cases. If the kernel will be packaged into Vivado or linked into an Alveo `xclbin`, validate interface metadata and integration at that boundary too.

## Version discipline

Use the repository's existing Vitis HLS command (`vitis_hls`, `vitis-run`, component workflow, Makefile, or Tcl) and match directives/API syntax to the installed release. Generated reports and database directories are build outputs unless the repository says otherwise; preserve scripts, configuration and compact summaries needed for reproduction.

Do not claim timing closure from an HLS clock estimate. Final timing, routing and resource behavior require the target Vivado/Vitis implementation.
