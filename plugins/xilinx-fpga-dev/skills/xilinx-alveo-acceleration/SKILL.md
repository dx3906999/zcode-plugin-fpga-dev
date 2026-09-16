---
name: xilinx-alveo-acceleration
description: Design, build, profile, or debug AMD Alveo accelerator systems using Vitis kernels, XRT host APIs, xclbin/platform files, PCIe, XDMA/QDMA, AXI, DMA batching, and host-device synchronization. Use for U250/V80 and other Alveo data-center cards; use the Vivado skill for RTL implementation details.
---

# Xilinx Alveo Acceleration

Treat acceleration as an end-to-end system: host call path, runtime/driver, PCIe/DMA, memory topology, kernel microarchitecture, correctness protocol and measurements.

## Freeze compatibility facts

Before changing code or builds, collect card model and serial/BDF when hardware is present, platform (`.xpfm`) identity, shell/firmware, XRT version, Vitis/Vivado version, host OS/kernel/IOMMU state, xclbin metadata, kernel names, connectivity configuration and repository build commands. Use `xrt-smi` or the release-appropriate legacy command read-only first. Never assume U250 and V80 share platforms, memory banks, shell interfaces or supported tool releases.

For architecture and measurement, read [references/architecture.md](references/architecture.md). For direct XDMA/QDMA design and safety, read [references/dma.md](references/dma.md).

## Preserve a software oracle

Keep a CPU or software-simulation backend with the same request/result ABI. Compare exact outputs, ordering, error behavior and boundary cases before performance claims. Separate functional equivalence from a trace-replay throughput model; queued/asynchronous checking is not equivalent to synchronous checking unless error delivery and program progress semantics are preserved.

## Optimize from a latency/bandwidth model

Measure host preparation, enqueue, DMA, kernel, completion polling/interrupt and result handling separately. Report warm-up, repetitions, batch/message size, concurrency, pinned/huge-page use, transfer direction, effective bytes and percentile latency when relevant. Distinguish theoretical link bandwidth, runtime API bandwidth and application useful throughput.

Prefer XRT and supported platform abstractions when they satisfy the contract. Choose direct XDMA/QDMA only when shell/control requirements justify owning driver/device nodes, descriptors, alignment, reset/recovery and security.

## Hardware mutation boundary

Device programming, hot/reset operations, firmware/shell changes, register or memory writes, and driver bind/unbind are material state changes. Perform them only when explicitly requested, after identifying the exact BDF/device and capturing the current state. Never run reset or firmware update as a generic troubleshooting step.
