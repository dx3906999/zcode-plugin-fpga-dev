# Board and card bring-up evidence order

Proceed from low-risk observations toward mutation:

- Verify power, cooling, cable/PCIe visibility, device identity and host logs.
- Record tool/runtime/driver, platform/shell/firmware, bitstream and probes metadata.
- Confirm configuration status and expected clocks/resets before functional traffic.
- Exercise a minimal known-safe datapath or vendor validation test appropriate to the exact platform.
- Compare host logs/counters with ILA/VIO evidence at the same transaction boundary.
- Change one variable, recapture, and retain the prior known-good state.

For Alveo, use `xrt-smi`/XRT diagnostics matching the installed release and record BDF/serial. Do not reset, flash, rebind a driver, or overwrite a programmed image as a generic diagnostic step. For remote `hw_server`, confirm that exclusive access and maintenance windows are within scope.
