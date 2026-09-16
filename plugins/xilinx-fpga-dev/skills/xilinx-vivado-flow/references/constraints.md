# XDC review guide

Constraints express the timing/environment contract. Do not use false paths or multicycle paths merely to make timing green.

## Clock and I/O checklist

- Define each primary clock at its real source with correct period and waveform.
- Define generated clocks where Vivado cannot derive the relationship or the design modifies phase/divide/multiply behavior.
- Model source-synchronous and system-synchronous interfaces with input/output delays derived from the external device, PCB budget, and clock relationship.
- Verify asynchronous clock groups reflect architecture. Synchronizer presence does not by itself justify grouping entire domains.
- Constrain configuration/control CDCs and data CDCs according to their actual protocol; review `report_cdc` rather than suppressing it globally.
- Obtain `PACKAGE_PIN`, bank voltage and `IOSTANDARD` from the exact board schematic/master XDC. Check differential pairs, clock-capable pins, GT quads/refclks and bank compatibility.

## Exception proof obligations

For every false path, identify the source, destination, reason timing analysis is inapplicable, and the mechanism ensuring functional correctness. For multicycle paths, state the launch/capture relationship and pair setup/hold adjustments correctly. Prefer narrow object collections and check matched object counts; an empty `get_*` query can silently invalidate intent.

## Evidence

Use the bundled `fpga_analyze_xdc` for a quick conservative summary, then validate in the target Vivado version with constraint parsing, `report_exceptions`, `report_clock_interaction`, `report_cdc`, `check_timing`, DRC and post-route timing. Static parsing cannot expand Tcl variables/loops or validate silicon pins.

Primary reference: AMD UG903 for the installed release, plus the target device and board documentation.
