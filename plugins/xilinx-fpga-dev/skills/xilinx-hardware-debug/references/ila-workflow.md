# ILA capture workflow

1. **Hypothesis**: write one falsifiable statement and the signal relationship that distinguishes it.
2. **Clock**: sample each ILA with a stable clock in the observed domain; synchronize cross-domain status before interpreting it.
3. **Probes**: include request, acceptance, response/error and enough identity (tag/address/length/state) to correlate a transaction.
4. **Trigger**: start simple and reachable. Use staged/advanced triggers only when capture probability demands them.
5. **Window**: reserve pre-trigger history for causes and post-trigger samples for consequences; estimate required cycles.
6. **Capture**: save raw data plus bitstream/LTX/build identity, trigger settings and expected result.
7. **Analysis**: qualify AXI/stream events only on valid handshakes; identify the first invariant failure.

An automated CSV analyzer can accelerate repetitive protocol checks, but it must know signal names, active levels, clock, expected ordering and field widths. The `fpga-claude` project is an optional MIT-licensed implementation for capturing/exporting ILA data through Vivado batch Tcl; assess compatibility with the installed Vivado/hw_server before adoption.

Primary sources: AMD Vivado Programming and Debugging Guide (UG908) and the matching ILA/VIO product guides.
