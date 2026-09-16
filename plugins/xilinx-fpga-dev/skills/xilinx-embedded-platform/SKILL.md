---
name: xilinx-embedded-platform
description: Build or debug AMD/Xilinx Zynq, Zynq UltraScale+ MPSoC, or Versal embedded platforms using XSA, Vitis Unified/XSCT, BSPs, bare-metal or FreeRTOS applications, PetaLinux, device trees, boot images, and XSDB/JTAG. Do not use for Alveo host acceleration or RTL-only implementation.
---

# Xilinx Embedded Platform

Maintain an explicit hardware-to-software handoff: Vivado exports the XSA; platform/domain/BSP consume it; applications consume generated headers/libraries; the boot image and Linux artifacts must all match that hardware identity.

## Establish the versioned handoff

Inspect the device/board, processing system, tool release, XSA path/hash/timestamp, processors/domains, OS, BSP, application, boot mode, memory map and repository automation. Determine whether the project uses classic XSCT or Vitis Unified Python/component APIs. Do not mix commands from different Vitis generations without a documented migration.

Use [references/vitis-workflow.md](references/vitis-workflow.md) for platform/application work and [references/petalinux.md](references/petalinux.md) for Linux/device-tree/boot artifacts.

## Regenerate coherently

When hardware addresses, interrupts, clocks or peripherals change, identify every generated consumer before rebuilding. Keep user source separate from generated BSP/platform output. Treat generated macro changes—such as device-ID versus base-address APIs—as versioned driver-interface changes, not blind search/replace targets.

Verify compile/link logs, BSP/domain identity, ELF sections/memory placement and hardware handoff. For Linux, verify device-tree bindings, reserved memory, clocks/interrupts, kernel config/modules and boot logs. Preserve the exact XSA and build command behind a result.

## State-changing gates

Programming FPGA/flash, downloading an ELF, writing target memory/registers, stopping a processor, modifying a boot device, or deploying to a remote board changes physical state. Perform it only when explicitly in scope after selecting the exact target and recording the current state/recovery path.

The community `vitis_mcp` surveyed by this plugin is not bundled because its inspected revision lacked an explicit license. Use standard repository scripts or vendor APIs unless the user separately chooses and approves an MCP integration.
