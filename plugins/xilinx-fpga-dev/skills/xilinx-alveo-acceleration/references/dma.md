# XDMA/QDMA decision and interface review

XDMA offers memory-mapped or streaming transfers with user/control BARs; QDMA adds queue-oriented descriptors and is a different host/device contract. Confirm which IP and shell actually exists before using driver APIs or device-node names.

## Design questions

- Who allocates/pins/maps DMA memory, and how is its lifetime synchronized?
- What are alignment, maximum transfer, scatter-gather and address-width limits?
- How are producer/consumer indices published, ordered and wrapped?
- What prevents overwrite of in-flight descriptors or stale completions?
- Are MMIO writes posted, and where are memory barriers/readbacks required?
- How are timeout, partial transfer, device reset and process crash recovered?
- What isolation prevents arbitrary host/device DMA outside approved buffers?
- Is polling justified by measured latency, CPU usage and core isolation versus interrupts?

## Batch experiments

Sweep 1, small powers of two, and the proposed operating range (for example 256–1024) without assuming the range is optimal. Vary payload size, queue depth, polling mode and direction. Report useful requests/s, bytes/s, CPU utilization and p50/p95/p99 completion latency. Ensure the same semantics and error visibility as the CPU oracle.

Use the exact driver/API matching the generated XDMA/QDMA IP release. The upstream Xilinx `dma_ip_drivers` repository is a reference, not proof that a deployed board shell exposes the same configuration.
