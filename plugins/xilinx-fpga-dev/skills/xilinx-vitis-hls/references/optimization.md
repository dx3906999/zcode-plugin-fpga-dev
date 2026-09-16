# HLS optimization loop

## Baseline

Record tool version, target, clock, top, exact test vector set, C-sim result, latency/II, resources and warnings. Confirm fixed-width signedness, overflow/rounding policy, aliasing assumptions, trip counts and array bounds.

## Diagnose before directing

- **II limited by dependency**: identify true versus false loop-carried dependencies; restructure state or prove independence before applying a dependence directive.
- **II limited by memory ports**: reshape storage, partition/bank arrays, batch accesses, widen interfaces or use streaming. Full partition can explode registers and routing.
- **Latency limited by loop structure**: pipeline the right level, flatten/merge when semantics permit, and unroll only when memory and downstream throughput support it.
- **Dataflow stalls**: inspect producer/consumer rates, FIFO depths, start propagation, task boundaries and deadlock conditions. Simulate backpressure and imbalanced stages.
- **Resource excess**: inspect operator sharing, unroll factors, arbitrary precision widths, array mapping, inlining and duplicated dataflow processes.
- **Clock failure**: distinguish operator delay from routing/fanout and memory inference. The HLS estimate is directional, not final sign-off.

## Acceptance

Require C simulation and co-simulation for behavior, synthesis report for HLS estimates, and downstream implementation for actual timing/resources. Compare against the baseline and explain the tradeoff rather than reporting only the improved metric.

Primary reference: AMD Vitis HLS UG1399 for the installed release.
