# Alveo architecture and performance evidence

## Contract checklist

- Request/result structs: fixed widths, packing, alignment, byte order, version/magic, sequence ID and error status.
- Ordering: in-order versus tagged completion, batch boundary, flush semantics, timeout and retry policy.
- Memory: host-only/device-only/host-visible buffers, migration/sync ownership, selected HBM/DDR bank, burst/alignment and cache coherency.
- Kernel: control protocol, CU count, AXI port/bundle mapping, outstanding transactions, stream depth and backpressure.
- Runtime: device selection, xclbin compatibility, context/queue ownership, event dependencies and process/thread safety.

## Performance model

For batch size `N`, model total latency as host preparation + fixed submission/DMA cost + transferred bytes/bandwidth + kernel service + completion/result handling. State whether operations overlap. A good throughput curve sweeps batch size and concurrency, reports saturation, and checks tail latency and correctness at every point.

## Evidence to retain

- `xrt-smi`/device query summary and XRT/Vitis/platform versions.
- Build/link commands and connectivity `.cfg`.
- xclbin metadata and target mode (`sw_emu`, `hw_emu`, `hw`).
- CPU affinity/NUMA placement, buffer sizes, iterations and timing method.
- Raw samples or machine-readable summary, not only averages.

Primary sources: Xilinx/XRT documentation and the matching Xilinx/Vitis_Accel_Examples release.
