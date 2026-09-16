# Vitis platform and application workflow

- Confirm the XSA was exported from the intended implemented hardware and whether it includes a bitstream.
- Enumerate processors, domains, OS/architecture and BSP drivers from the generated platform instead of assuming names.
- Match application templates and driver APIs to the installed release. Prefer base-address/device-tree-derived APIs where the generated BSP does so.
- Keep platform generation, BSP configuration, application import and build reproducible through the repository's existing Tcl/Python/CLI path.
- On link failures, inspect the linker script, memory regions, section sizes, startup code, libraries and processor architecture.
- On target failures, separate FPGA configuration, processor reset/state, memory download, cache/MMU and peripheral-clock/reset causes.

Primary sources are the Vitis Unified Software Platform documentation and the board/device TRM for the installed release. AMD's `ai-assisted-vitis` repository provides useful migration examples but is not a substitute for version-matched APIs.
