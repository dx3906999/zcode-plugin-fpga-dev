# Vivado workflow and evidence gates

Choose project mode when the repository owns an `.xpr`, uses managed IP/block designs, or relies on run strategies. Choose non-project mode when the checked-in Tcl explicitly reads sources/constraints and invokes synthesis/implementation commands. Do not silently convert between them.

## Stage gates

1. **Elaboration/simulation**: compile the actual source order with project defines/include paths; test reset, nominal transactions, backpressure, boundary lengths, and error behavior relevant to the change.
2. **Synthesis**: require a completed run, no unexplained critical warnings, expected clock inference, and plausible LUT/FF/BRAM/URAM/DSP usage. Look for trimmed logic, inferred latches, combinational loops, multi-driven nets and width truncation.
3. **Implementation**: require placement and routing completion. Capture `report_timing_summary`, `report_utilization`, `report_drc`, and when relevant `report_methodology`, `report_cdc`, clock utilization and congestion.
4. **Bitstream**: gate on implementation completion, DRC classification, timing constraints coverage, exact part/platform, and expected `.bit`/`.ltx` pairing. A forced bitstream is an explicit exception and must retain the warnings that motivated the force.

## Reproducible Tcl properties

- Resolve paths relative to the script location rather than the caller's current directory.
- Parameterize part, top, jobs and output directory when the repository supports variants.
- Use deterministic report and checkpoint names.
- Check command/run status and return non-zero on failure.
- Never assume `reset_run` or deletion of generated directories is harmless; inspect existing outputs and user changes first.
- Quote/list Tcl paths safely. Avoid interpolating untrusted text as executable Tcl.

## Timing closure loop

Preserve a baseline before changing RTL, constraints, strategy, placement or physical optimization. Compare WNS/TNS, failing endpoints, path group, logic depth, clock skew/uncertainty, fanout and congestion. Fix invalid/missing constraints before optimizing logic. Prefer architectural fixes—pipelining, fanout replication, RAM/DSP inference, CDC correction—over directive roulette. Test one coherent hypothesis per iteration.

AMD primary references: UG894 (Tcl scripting), UG901 (synthesis), UG904 (implementation), UG906 (design analysis and timing closure), UG949 (methodology), and UG835 (Tcl command reference). Match the documentation release to the installed Vivado version.
