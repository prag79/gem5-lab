# gem5 Lab — Student Tutorial

This lab teaches you what gem5 is and how to run it, in three stages
of increasing complexity. You don't need to install anything on your
laptop. You don't need to understand C++, Python, or computer
architecture before starting — you'll pick those up as you go.

Total time: about 30 minutes if everything cooperates.

---

## Step 0 — Open the lab in GitHub Codespaces

Click the badge on the [repo's README](README.md) (or open the repo
on GitHub and press **Code → Codespaces → Create codespace on main**).

A browser-based VS Code window opens. Wait ~30 seconds for the
container to come up. When you see a terminal prompt that looks like:

```
student@codespaces-xxxxxx:/workspaces/gem5-lab$
```

you're ready. Everything below runs in that terminal.

> **Why a codespace?** gem5 is a 4-million-line C++ simulator with
> Python bindings, a RISC-V cross-compiler, and a small mountain of
> system libraries. Setting that up on a laptop takes hours. The
> codespace ships a prebuilt container with all of it ready.

---

## Lab 01 — Hello, simulated RISC-V

> One static RV64 binary, run on the simplest possible gem5 board
> in **syscall-emulation (SE) mode**. This is the smallest end-to-end
> gem5 invocation that prints something.

Run:

```bash
lab 01
```

What happens:

1. gem5 cross-compiles `hello-se.c` → `hello-se.elf` (a static RV64 ELF).
2. gem5 boots a 1-core ATOMIC RISC-V processor with 64 MiB of RAM.
3. The simulated CPU runs your binary; `printf` is forwarded to the
   host via syscall emulation.
4. When the binary returns, gem5 prints simulation stats and exits.

You should see, near the bottom of the output:

```
*** Hello from gem5 SE-mode RV64 ***
printf goes via syscall emulation.
```

### Inspect the stats

gem5 wrote a stats file. Have a look:

```bash
cd ~/work/01-se-hello
head -40 m5out/stats.txt
grep -E "numCycles|committedInsts" m5out/stats.txt
```

`numCycles` is simulated CPU cycles. `committedInsts` is RISC-V
instructions retired. Their ratio (CPI = cycles ÷ insts) is one of
the most fundamental microarchitecture metrics — for ATOMIC it'll be
exactly 1.0 because that model assumes perfect 1-IPC execution.

### Edit and re-run

Your work lives at `~/work/01-se-hello/` and survives codespace
rebuilds. Edit `run-se.py` to change `CPUTypes.ATOMIC` to
`CPUTypes.TIMING`, then:

```bash
lab 01
```

Compare the new `m5out/stats.txt` against the previous run. Numbers
move — that's gem5 doing its job.

---

## Lab 02 — Boot Linux on a simulated HiFive board (FS mode)

> Full-system simulation: gem5 boots a real RV64 Linux kernel +
> BusyBox userland on a HiFive Unmatched board model. The simulated
> UART is exposed on a TCP port you connect to with `telnet`.

You'll need **two terminals** for this lab. In VS Code: split your
terminal panel (or open a new one with the `+` button).

### Terminal 1: start the simulation

```bash
lab 02
```

First time only, this downloads ~24 MB of kernel + disk image from
`dist.gem5.org`. Then gem5 starts and prints:

```
Beginning simulation!
Global frequency set at 1000000000000 ticks per second
info: Listening for system connection on port 3456
**** REAL SIMULATION ****
```

Leave this terminal alone — gem5 is now simulating Linux booting.

### Terminal 2: connect to the simulated UART

```bash
telnet localhost 3456
```

You'll immediately see:

```
==== m5 terminal: Terminal 0 ====
```

…and then **silence for several minutes**. That's normal. The
simulated CPU is booting Linux one cycle at a time. On a Codespaces
VM, expect the first boot output to appear after **2–5 minutes**, and
a `login:` prompt after **10–20 minutes**.

> **Why so slow?** The default CPU model (`TIMING`) models pipeline
> stalls realistically. If you don't care about realistic stats and
> just want to see Linux boot quickly, edit
> `~/work/02-fs-linux-riscv/run-fs.py` and change `CPUTypes.TIMING`
> to `CPUTypes.ATOMIC`. Boot drops to ~30–60 seconds.

When the prompt appears:

```
buildroot login:
```

Login as `root` (no password). You're now inside a real Linux running
on a simulated CPU. Try:

```sh
uname -a
cat /proc/cpuinfo
m5 exit
```

`m5 exit` is gem5's special instruction. The simulated guest tells
the simulator "we're done"; gem5 stops cleanly and writes its final
`m5out/stats.txt` in Terminal 1.

### What you just did

Every memory access, every cache miss, every branch prediction
during that Linux boot is recorded in `m5out/stats.txt`. You can
correlate Linux's boot phases against microarchitectural events. In
~5 lines of script, gem5 gave you the kind of visibility you'd
otherwise need an FPGA prototype or a $50k logic analyzer for.

---

## Lab 03 — Same binary, two CPU models, different stats

> The headline gem5 demo. Run **the same** RV64 binary on
> `AtomicSimpleCPU` (idealized 1-IPC) and `O3CPU` (full out-of-order
> superscalar). Watch the cycles-per-instruction diverge.

Run:

```bash
lab 03
```

What happens:

1. gem5 cross-compiles `hello-se.c` → `hello-se.elf` (a small RV64
   binary with a printf and a 10k-iteration sum loop, to make the
   cycle counts non-trivial).
2. gem5 runs it under `ATOMIC`. Stats land in `m5out-atomic/`.
3. gem5 runs it again under `O3`. Stats land in `m5out-o3/`. This
   step is slower — O3 simulates every pipeline stage.
4. `compare.py` parses both `stats.txt` files and prints a JSON
   summary.

You'll see something like:

```
=== Summary ===
{
  "atomic": { "cycles": 12345, "insts": 12345, "cpi": 1.0000 },
  "o3":     { "cycles":  9876, "insts": 12345, "cpi": 0.8000 }
}
```

Same number of instructions in both cases (it's the same binary).
But the cycle count differs — O3 finds parallelism Atomic cannot
expose, so its CPI is < 1.0.

That gap is the whole point of microarchitecture as a discipline.

### Going further

- Edit `~/work/03-cpu-comparison/compare.py` and add a `("timing",
  "TIMING")` case to compare three CPU models.
- Edit `hello-se.c` to do something more interesting (matrix multiply,
  pointer chasing, branchy code) and watch how each CPU model handles
  it.
- Sweep cache configurations and plot the results with `matplotlib`
  (already installed in the container).

---

## Reference

### One-line recap

| Lab | Command | What you'll do |
|---|---|---|
| 01 | `lab 01` | Build + run a hello binary in SE mode |
| 02 | `lab 02` (terminal 1) + `telnet localhost 3456` (terminal 2) | Boot Linux on a simulated RISC-V SoC |
| 03 | `lab 03` | Compare CPI of ATOMIC vs O3 on the same binary |

### Where things live

| Path | What |
|---|---|
| `/labs/0N-*/` | Canonical lab content (read-only, baked into the image) |
| `~/work/0N-*/` | Your editable working copy (persisted across codespace restarts) |
| `~/work/0N-*/m5out*/` | gem5's per-run output: `stats.txt`, `config.ini`, log |
| `gem5-riscv` | The gem5 simulator binary built for the RISC-V ISA |
| `riscv64-linux-gnu-gcc` | Cross-compiler for the RISC-V Linux ABI |

### Useful commands

```bash
lab list                              # show available labs
lab shell                             # drop into a bash shell
gem5-riscv --help                     # gem5 binary options
gem5-riscv --copyright                # legal notice
ls /opt/gem5/configs/example/         # gem5's bundled example configs
```

### Stopping and restarting

- Closing the browser tab does **not** stop the codespace. It keeps
  running and gets billed against your free Codespaces hours.
- To stop it: GitHub → top-right avatar → **Your codespaces** →
  three-dot menu → **Stop codespace**.
- To resume: same menu, **Open in browser**. Your `~/work/` is
  preserved exactly as you left it.
- Codespaces auto-stop after 30 minutes idle by default.

### When something breaks

- Stats look wrong? Make sure you re-ran `lab N` after editing — it
  re-runs gem5 from scratch each time.
- gem5 takes too long to boot Linux? Switch the CPU type to
  `ATOMIC` in `~/work/02-fs-linux-riscv/run-fs.py`.
- Something in `~/work/` is in a weird state? Just `rm -rf
  ~/work/0N-*` and re-run `lab N` — the canonical content is restored
  from `/labs/`.
- Anything else? Open an issue on the repo with the full output.
