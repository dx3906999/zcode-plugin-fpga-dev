# Tool selection

| Need | Preferred starting point | Boundary |
|---|---|---|
| SystemVerilog syntax/style/format | Verible | No project-wide semantic elaboration proof. |
| Fast synthesizable SV lint/simulation | Verilator | Check unsupported timing/testbench/UVM constructs and vendor libraries. |
| Lightweight Verilog simulation | Icarus Verilog | Smaller SystemVerilog feature set; keep a vendor/Verilator lane when needed. |
| Python testbench and scoreboards | cocotb with an already-supported simulator | Pin compatible simulator/cocotb versions in CI. |
| Formal safety/liveness checks | SymbiYosys/Yosys with suitable engine | Review assumptions, depth, induction status and unsupported constructs. |
| Xilinx IP/primitives and release fidelity | XSim via Vivado flow | Tool availability/licensing and longer startup cost. |
| Portable core/build metadata | FuseSoC/Edalize | Adopt only when it reduces an existing multi-backend problem. |

Never silently switch simulators to get a passing result. Document semantic limitations and keep the authoritative lane for the design.
