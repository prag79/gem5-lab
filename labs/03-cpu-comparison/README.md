# Lab 03 — Compare CPU models (the gem5 payoff)

Run the same RV64 hello workload twice — once on `AtomicSimpleCPU`
(1 IPC, no timing) and once on `O3CPU` (out-of-order superscalar) —
and print the CPI side by side.

## Run it

```bash
lab 03
```

You'll see something like:

```
=== Summary ===
{
  "atomic": { "cycles": 12345, "insts": 12345, "cpi": 1.0000 },
  "o3":     { "cycles":  9876, "insts": 12345, "cpi": 0.8000 }
}
```

The exact numbers vary by gem5 version; the **shape** is the lesson.
Same binary, same memory, only the CPU pipeline model changed — and
you can quantify what an OoO core buys you in IPC.

## Going further

- Re-run with different `--cpu-type` values (gem5 supports
  `ATOMIC`, `TIMING`, `O3`, `MINOR`).
- Edit `compare.py` to add a third case and grep for cache miss
  rates as well as CPI.
- Wrap it in a sweep over cache sizes and plot `miss_rate vs size`
  with matplotlib — that single graph is half a microarchitecture
  course.
