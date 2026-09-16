# HLS interface decisions

Choose from the system contract, not convenience:

- `ap_ctrl_hs` suits start/done transactions; free-running streaming kernels need the release-appropriate control mode and reset behavior.
- AXI4-Stream requires explicit `TVALID/TREADY` backpressure reasoning, packet framing (`TLAST` when applicable), width/sideband agreement and bounded buffering.
- AXI4 master ports need aligned/burst-friendly accesses, stable bundle mapping, realistic outstanding transactions and host-visible buffer semantics.
- AXI4-Lite control maps need a documented register/offset contract, ownership and update semantics. Do not let host and RTL independently guess generated addresses.
- Direct memory/BRAM interfaces require port-conflict analysis and clear arbitration when shared.

For a batched offload engine, specify request/result record layout, byte order, alignment, maximum batch, completion/error behavior and ordering. Model DMA setup cost separately from steady-state bandwidth. An asynchronous batching optimization must not change a synchronous correctness contract unless the caller/runtime is redesigned to tolerate it.
