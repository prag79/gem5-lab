# Lab 01 — SE-mode hello on RV64

The simplest gem5 invocation. A static `hello` binary runs under
**syscall emulation** on a `SimpleBoard` with one ATOMIC RISC-V core.

## Run it

```bash
lab 01
```

You should see:

```
*** Hello from gem5 SE-mode RV64 ***
printf goes via syscall emulation.
```

When the program exits, gem5 writes `m5out/stats.txt` in the current
directory.

## Inspect the stats

```bash
head -40 m5out/stats.txt
grep -E "numCycles|committedInsts|cpi" m5out/stats.txt
```

## Modify and re-run

Copy this lab into your work folder so changes survive a Codespace
rebuild:

```bash
cp -r /labs/01-se-hello ~/work/01
cd ~/work/01
```

Then edit `run-se.py` — for example, swap `CPUTypes.ATOMIC` for
`CPUTypes.TIMING` and re-run:

```bash
make
gem5-riscv run-se.py hello-se.elf
```

Compare the new `m5out/stats.txt` against the original.
