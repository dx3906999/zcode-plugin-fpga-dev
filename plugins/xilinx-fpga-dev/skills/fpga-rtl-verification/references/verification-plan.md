# Minimum verification dimensions

Map tests/properties to the design contract rather than generating generic stimulus.

- Reset: assertion/deassertion timing, synchronous/asynchronous semantics, reset during activity, output validity after reset.
- Handshake: stability while stalled, no transfer without both sides ready/valid, ordering, backpressure, bubbles and continuous traffic.
- FIFOs/queues: empty/full boundaries, simultaneous enqueue/dequeue, overflow/underflow prevention, pointer wrap, CDC assumptions.
- Width/length: zero or minimum lengths where legal, maximum, boundary crossing, partial final beats, byte strobes and sign extension.
- Errors: malformed requests, timeouts, downstream failures, recovery and sticky/clear status behavior.
- CDC: structural synchronizers plus protocol-level coherence; reconvergence and reset-domain crossings deserve explicit review.
- Parameterization: representative minima/maxima and invalid-parameter compile-time checks.

Assertions should express local invariants; a scoreboard should establish end-to-end data/order. Functional coverage or a documented test matrix explains which state space the regression actually exercises.
