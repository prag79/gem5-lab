# gem5 Lab

Three guided exercises in computer-architecture simulation with
[gem5](https://www.gem5.org/), running entirely in your browser via
GitHub Codespaces. No local install required — no toolchain, no
Python, no gem5 source tree to build.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/prag79/gem5-lab?quickstart=1)

---

## Table of contents

- [What you'll learn](#what-youll-learn)
- [Open the codespace](#open-the-codespace)
- [Lab 01 — Hello, simulated RISC-V (SE mode)](#lab-01--hello-simulated-risc-v-se-mode)
- [Lab 02 — Boot Linux on a simulated HiFive board (FS mode)](#lab-02--boot-linux-on-a-simulated-hifive-board-fs-mode)
- [Lab 03 — Same binary, two CPU models, different stats](#lab-03--same-binary-two-cpu-models-different-stats)
- [Editing labs and re-running](#editing-labs-and-re-running)
- [Reference: paths, commands, and stopping the codespace](#reference)
- [Troubleshooting](#troubleshooting)
- [What's inside the container](#whats-inside-the-container)

---

## What you'll learn

- How to invoke gem5 end-to-end from a Python script.
- The difference between **SE-mode** (syscall emulation, runs a single
  static binary) and **FS-mode** (full-system, boots a real OS).
- How to read gem5's `m5out/stats.txt` — cycles, instructions, CPI.
- Why the same binary's CPI changes when you swap CPU pipeline models
  (ATOMIC → O3) — the headline argument for microarchitecture as a
  field.

You don't need to know C++, gem5 internals, or computer architecture
beforehand. You'll pick those up as you go. Total time: ~30 minutes
if everything cooperates.

---

## Open the codespace

You need a GitHub account (free is fine) and ~2 minutes of patience.

### Step 1 — launch

Click the **Open in GitHub Codespaces** badge above. A dialog asks
which branch and machine type to use; the defaults (main, 4-core) are
correct. Click **Create codespace**.

> Alternative: from the GitHub repo page, click **Code → Codespaces
> → Create codespace on main**.

### Step 2 — wait for the container

A browser-based VS Code window opens. The first time you launch this
codespace, GitHub:

1. Provisions a fresh Ubuntu VM (~15 s).
2. Pulls the prebuilt gem5 lab image from GHCR (~30–60 s).
3. Starts the container and attaches you to it.

When you see a terminal panel with a prompt that looks like:

```
student@codespaces-xxxxxx:/workspaces/gem5-lab$
```

…you're ready. Everything below runs in that terminal.

### Step 3 — sanity check

```bash
lab list
```

You should see:

```
Available labs:
  01-se-hello
  02-fs-linux-riscv
  03-cpu-comparison

Run with: lab 01 | lab 02 | lab 03
Working copies live under: /home/student/work/<lab-name>/
```

If you see that, you're set. If not, jump to [Troubleshooting](#troubleshooting).

---

## Lab 01 — Hello, simulated RISC-V (SE mode)

> The smallest end-to-end gem5 invocation that prints something.
> One static RV64 binary, run on a 1-core ATOMIC RISC-V processor
> with 64 MiB of RAM, in **syscall emulation** mode.

### Run

```bash
lab 01
```

Under the hood this:

1. Cross-compiles `hello-se.c` → `hello-se.elf` with
   `riscv64-linux-gnu-gcc -O2 -static`.
2. Boots a `SimpleBoard` with one ATOMIC RISC-V core and 64 MiB DDR3.
3. Runs the binary; `printf` is forwarded to the host via syscall
   emulation.
4. Prints simulation stats and exits.

You'll see, near the bottom of the output:

```
*** Hello from gem5 SE-mode RV64 ***
printf goes via syscall emulation.
```

### Inspect the stats

```bash
cd ~/work/01-se-hello
head -40 m5out/stats.txt
grep -E "numCycles|committedInsts" m5out/stats.txt
```

- `numCycles` — simulated CPU cycles.
- `committedInsts` — RISC-V instructions retired.
- Their ratio (CPI = cycles ÷ insts) is one of the most fundamental
  microarchitecture metrics. For the ATOMIC model it's exactly 1.0
  by construction (it assumes perfect 1-IPC execution).

### Edit and re-run

Your work lives at `~/work/01-se-hello/` and **survives codespace
restarts**. Open `run-se.py` in the editor and change:

```python
cpu_type=CPUTypes.ATOMIC,
```

to:

```python
cpu_type=CPUTypes.TIMING,
```

Then re-run `lab 01`. Compare the new `m5out/stats.txt` against the
previous run — the cycle count will move because TIMING actually
models memory-access latency.

---

## Lab 02 — Boot Linux on a simulated HiFive board (FS mode)

> Full-system simulation: gem5 boots a real RV64 Linux kernel +
> BusyBox userland on a HiFive Unmatched board model. The simulated
> UART is exposed on a TCP port you connect to with `telnet`.

You'll need **two terminals** for this lab. In VS Code: split your
terminal panel (right-click → Split, or click the `+` button next to
the terminal dropdown).

### Terminal 1 — start the simulation

```bash
lab 02
```

First time only, this downloads ~24 MB of kernel + disk image from
`dist.gem5.org` (cached in `~/work/02-fs-linux-riscv/` for next time).
Then gem5 starts and prints:

```
Beginning simulation!
Global frequency set at 1000000000000 ticks per second
info: Listening for system connection on port 3456
**** REAL SIMULATION ****
```

Leave this terminal alone — gem5 is now simulating Linux booting.

### Terminal 2 — connect to the simulated UART

```bash
telnet localhost 3456
```

You'll immediately see:

```
==== m5 terminal: Terminal 0 ====
```

…and then **silence for several minutes**. That is normal. The
simulated CPU is booting Linux one cycle at a time. On a Codespaces
VM, expect the first kernel output to appear after **2–5 minutes**,
and a `login:` prompt after **10–20 minutes**.

> **Why so slow?** The default CPU model (`TIMING`) models memory
> latency realistically. If you don't care about realistic stats and
> just want to *see* Linux boot quickly, edit
> `~/work/02-fs-linux-riscv/run-fs.py` and change `CPUTypes.TIMING`
> to `CPUTypes.ATOMIC`. Boot drops to ~30–60 seconds.

When the prompt appears:

```
buildroot login:
```

Login as **`root`** with no password. You're now inside a real Linux
running on a simulated CPU. Try:

```sh
uname -a
cat /proc/cpuinfo
m5 exit
```

`m5 exit` is gem5's special "we're done" instruction. The simulated
guest tells the simulator to stop; gem5 cleanly shuts down and writes
its final `m5out/stats.txt` in Terminal 1. Both terminals return to a
shell prompt.

### What you just did

Every memory access, every cache miss, every branch prediction
during that Linux boot is recorded in `m5out/stats.txt`. You can
correlate Linux's boot phases against microarchitectural events. In
under 100 lines of Python, gem5 gave you the kind of visibility you'd
otherwise need an FPGA prototype or a $50k logic analyzer for.

---

## Lab 03 — Same binary, two CPU models, different stats

> The headline gem5 demo. Run **the same** RV64 binary on
> `AtomicSimpleCPU` (idealized 1-IPC) and `O3CPU` (full out-of-order
> superscalar). Watch the cycles-per-instruction diverge.

### Run

```bash
lab 03
```

Under the hood:

1. Cross-compiles `hello-se.c` → `hello-se.elf` (a small RV64 binary
   with a printf and a 10 000-iteration sum loop, to make the cycle
   counts non-trivial).
2. Runs it under `ATOMIC`. Stats land in `m5out-atomic/`.
3. Runs it again under `O3`. Stats land in `m5out-o3/`. This step is
   slower (~30–60 s) because O3 simulates every pipeline stage.
4. Parses both `stats.txt` files and prints a JSON summary.

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
- Edit `hello-se.c` to do something more interesting (matrix
  multiply, pointer chasing, branchy code) and watch how each CPU
  model handles it.
- Sweep cache configurations and plot the results with `matplotlib`
  (already installed in the container).

---

## Editing labs and re-running

The first time you run `lab N`, the dispatcher copies the canonical
lab content from `/labs/0N-*/` (read-only, baked into the image) to
`~/work/0N-*/` (your editable, persisted workspace), then runs from
there. Any subsequent `lab N` invocation uses `cp -ru` (update only
if source is newer), so **your edits in `~/work/` are never
overwritten** — only files that don't exist in your workdir get
copied in fresh.

### Quickest workflow: just re-run `lab N`

After editing any file in `~/work/0N-*/`, simply re-run the same
dispatcher command. It rebuilds and re-simulates from scratch:

| You edited… | Re-run with | What happens |
|---|---|---|
| Lab 01: `hello-se.c` or `run-se.py` | `lab 01` | `make` rebuilds the ELF if needed, gem5 re-runs |
| Lab 02: `run-fs.py` | `lab 02` | Artifacts already cached, gem5 re-runs immediately |
| Lab 03: `hello-se.c`, `run-se.py`, or `compare.py` | `lab 03` | `make` rebuilds the ELF, both ATOMIC and O3 re-run |

### Finer control: drive `make` and `gem5-riscv` directly

For tighter iteration loops where you don't want a full rebuild +
both CPU runs every time, drop into the workdir and invoke the tools
yourself.

#### Lab 01

```bash
cd ~/work/01-se-hello

make                                  # only rebuilds hello-se.elf if hello-se.c changed
gem5-riscv run-se.py hello-se.elf     # one gem5 run, output to ./m5out/
```

To keep multiple runs side-by-side for comparison:

```bash
gem5-riscv --outdir m5out-atomic run-se.py hello-se.elf
# ...edit run-se.py, swap CPUTypes.ATOMIC -> CPUTypes.TIMING...
gem5-riscv --outdir m5out-timing run-se.py hello-se.elf
diff m5out-atomic/stats.txt m5out-timing/stats.txt | less
```

#### Lab 02

```bash
cd ~/work/02-fs-linux-riscv

make artifacts                        # no-op if kernel + disk already cached
gem5-riscv run-fs.py                  # boot Linux; from a 2nd terminal:
                                      #   telnet localhost 3456
```

Force-refresh the kernel and disk image (rare):

```bash
make clean && make artifacts
```

#### Lab 03

```bash
cd ~/work/03-cpu-comparison

make                                  # rebuilds hello-se.elf if hello-se.c changed
python3 compare.py                    # runs both ATOMIC and O3, prints JSON
```

Or run just one CPU model to iterate fast:

```bash
gem5-riscv --outdir m5out-atomic run-se.py hello-se.elf --cpu-type ATOMIC
gem5-riscv --outdir m5out-o3     run-se.py hello-se.elf --cpu-type O3
```

`run-se.py` accepts `--cpu-type` ∈ {`ATOMIC`, `TIMING`, `O3`,
`MINOR`}.

### Watch out for these

- **`m5out/` is overwritten on every gem5 run.** If you want to keep
  a particular run's stats, copy it aside first
  (`cp -r m5out m5out-baseline`) or always pass `--outdir
  m5out-<label>` to gem5.
- **`make clean`** in any lab dir deletes the built ELF and any
  `m5out*/` directories — useful if a stale binary is confusing you.
- **Reset a lab to canonical state:**
  `rm -rf ~/work/0N-* && lab 0N`. The next `prepare_workdir` re-copies
  fresh from `/labs/`.
- **Edits to Python files** (`run-se.py`, `run-fs.py`, `compare.py`)
  take effect on the next gem5/python invocation — no build step
  needed.

---

## Reference

### Commands at a glance

| Command | What it does |
|---|---|
| `lab list` | Show available labs |
| `lab 01` | Build + run the SE-mode hello |
| `lab 02` | Boot Linux on the HiFive board (use with `telnet localhost 3456` in a 2nd terminal) |
| `lab 03` | Compare CPI of ATOMIC vs O3 on the same binary |
| `lab shell` | Drop into an interactive bash shell |
| `lab help` | Print usage |
| `gem5-riscv --help` | gem5 binary options |
| `gem5-riscv --copyright` | Legal notice |

### Where things live

| Path | What |
|---|---|
| `/labs/0N-*/` | Canonical lab content (read-only, baked into the image) |
| `~/work/0N-*/` | Your editable working copy (persisted across codespace restarts) |
| `~/work/0N-*/m5out*/` | gem5's per-run output: `stats.txt`, `config.ini`, log |
| `/opt/gem5/bin/gem5-riscv` | The gem5 simulator binary built for the RISC-V ISA |
| `/opt/gem5/bin/gem5-x86`, `gem5-arm` | gem5 binaries for X86 and ARM (also pre-built) |
| `/opt/gem5/configs/` | gem5's bundled example configs |
| `/opt/gem5/python/gem5/` | gem5 Python stdlib (already on `PYTHONPATH`) |
| `riscv64-linux-gnu-gcc` | Cross-compiler for the RISC-V Linux ABI |

### Stopping and resuming the codespace

- Closing the browser tab does **not** stop the codespace. It keeps
  running and gets billed against your free Codespaces hours (60h/mo
  on GitHub Free, 180h/mo on Pro).
- To stop: GitHub → top-right avatar → **Your codespaces** → three-dot
  menu next to your codespace → **Stop codespace**.
- To resume: same menu → **Open in browser**. Your `~/work/`,
  including any cached lab artifacts, is preserved exactly as you
  left it.
- Codespaces auto-stop after 30 minutes idle by default.
- To delete a codespace and free the storage: same menu → **Delete**.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `lab` command not found | Wait ~10 more seconds for the container to finish attaching, or open a new terminal. |
| Lab 02 telnet shows the banner then nothing for minutes | Normal. TIMING-model Linux boot takes 10–20 min on Codespaces. Switch to `CPUTypes.ATOMIC` in `~/work/02-fs-linux-riscv/run-fs.py` for ~30 s boot. |
| `make` fails with `Permission denied` writing to `/labs/...` | You're an out-of-date image. Run `gh codespace rebuild --full` or recreate the codespace. |
| `riscv64-linux-gnu-gcc: stdio.h: No such file` | Same as above — old image. |
| `gem5-riscv: error while loading shared libraries` | Same as above. |
| Anything in `~/work/` is in a weird state | `rm -rf ~/work/0N-*` and re-run `lab N` — the canonical content is restored from `/labs/`. |
| Anything else | Open an issue on this repo with the full output. |

---

## What's inside the container

The codespace runs a Docker image (`ghcr.io/prag79/gem5-lab:latest`)
built from [`.devcontainer/Dockerfile`](.devcontainer/Dockerfile).
It contains:

- gem5 v23.0.1.0 built for X86, ARM, and RISC-V (`gem5.opt`
  optimization level).
- The gem5 standard Python library at `/opt/gem5/python/`.
- The Ubuntu RISC-V cross toolchain (`gcc-riscv64-linux-gnu`,
  `binutils-riscv64-linux-gnu`, `libc6-dev-riscv64-cross`).
- Python 3.10, plus `matplotlib` and `pandas` for stats analysis.
- The `lab` dispatcher script at `/usr/local/bin/lab`, and the lab
  content under `/labs/`.

The image is rebuilt automatically on every push to `main` that
touches `.devcontainer/Dockerfile`, `lab`, or anything under `labs/`,
via [`.github/workflows/build.yml`](.github/workflows/build.yml).

The lab content itself (Python configs, `hello-se.c`, the `lab`
dispatcher) lives in this repository under [`labs/`](labs/) and the
top-level [`lab`](lab) script. Each lab also has its own `README.md`
under `labs/<name>/` if you want to dig deeper.
