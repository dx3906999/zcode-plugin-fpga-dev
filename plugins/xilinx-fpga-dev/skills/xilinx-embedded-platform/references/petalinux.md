# PetaLinux and boot artifact checklist

Track the chain `XSA -> project/config -> device tree -> kernel/rootfs -> BOOT.BIN/image.ub -> deployed media`. A successful build does not prove the deployed media contains those outputs.

- Preserve user layers/recipes, device-tree overlays and configuration fragments; generated work directories are rebuildable outputs.
- Validate each custom peripheral's `compatible`, register range, interrupts, clocks/resets, DMA/coherency and reserved-memory contract against RTL/XSA.
- Record boot mode and image composition (FSBL/PLM, PMUFW where applicable, bitstream, ATF, U-Boot, ELF).
- On boot failure, retain the earliest serial log and classify ROM/FSBL/PLM, firmware, U-Boot, kernel, device-tree, rootfs or application stage.
- Do not solve a device-tree ownership conflict by editing generated files that will be overwritten; place changes in the supported user layer.
- Cross-building and deployment over SSH can use ordinary scoped tools; a generic unrestricted SSH MCP is intentionally not part of this plugin.

Use PetaLinux and Versal/Zynq boot documentation matched to the installed release and exact board.
