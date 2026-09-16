---
name: xilinx-hardware-debug
description: Debug AMD/Xilinx FPGA hardware with Vivado Hardware Manager, hw_server, JTAG, ILA/VIO, probes files, trigger/capture plans, board bring-up, and waveform evidence. Use when a programmed physical FPGA or captured ILA data is involved; use RTL verification for pre-hardware simulation.
---

# Xilinx Hardware Debug

Convert a hardware symptom into a bounded, repeatable capture with a clear expected invariant.

## Identify the exact target

Record board/card, cable or remote `hw_server`, device index/BDF/serial, bitstream, matching `.ltx`, build timestamp/hash, clocks/resets and observed symptom. Read device state before mutation. Multiple boards or devices require an unambiguous target; do not select the first device by habit.

Use [references/ila-workflow.md](references/ila-workflow.md) for instrumentation and capture design. Use [references/bringup.md](references/bringup.md) for first-board checks and evidence ordering.

## Plan observability before capturing

State the hypothesis, relevant clock domain, trigger condition, probes, widths, capture depth, trigger position and expected waveform relation. Prefer protocol-level probes such as valid/ready, address/length, state, error and FIFO occupancy over large undirected signal sets.

Changing trigger expression, position, or a capture window within the implemented ILA capability normally does not require a new bitstream. Adding/removing probes, changing widths/depth, or inserting/removing ILA logic changes the implemented design and requires synthesis/implementation/bitstream generation.

## Analyze as evidence

Preserve raw `.wdb`/CSV and metadata before filtering. Align events to the sampled clock, account for trigger latency and qualify transfers with the protocol handshake. Report the earliest violated invariant and distinguish cause from downstream effects. If the capture cannot discriminate hypotheses, propose the smallest instrumentation change.

## Physical-state gate

Programming a bitstream, driving VIO outputs, writing registers/memory, resetting a board/card, or changing firmware is a material state change. Do it only when explicitly requested and after resolving the exact target. Keep a recovery path and current-state record. Never program a bitstream whose part/platform or `.ltx` association is uncertain.
