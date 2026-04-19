# Lab 02 — Boot Linux on a HiFive board (RISC-V FS mode)

Full-system simulation: gem5 boots a real RV64 Linux kernel + BusyBox
disk image on a HiFive Unmatched board model. The simulated UART is
exposed on TCP port **3456**.

> First run downloads the kernel (`bootloader-vmlinux-5.10`, ~13 MB)
> and the BusyBox disk image (`riscv-disk.img.gz`, ~11 MB compressed)
> from `dist.gem5.org` into `~/work/02-fs-linux-riscv/`. Subsequent
> runs reuse the local copy. We fetch directly via `make artifacts`
> instead of using `obtain_resource()`, because the gem5-resources
> metadata service no longer responds to v23.0.1.0 clients (HTTP 410).

## Run it

In your **first terminal**:

```bash
lab 02
```

gem5 prints:

```
Global frequency set at 1000000000000 ticks per second
info: Listening for system connection on port 3456
**** REAL SIMULATION ****
```

In a **second terminal** (right-click the terminal panel → "New
Terminal" inside the same Codespace):

```bash
telnet localhost 3456
```

Watch OpenSBI → kernel boot → BusyBox login over the next ~60 s.

## Once you have a login

Login as `root` (no password). Try:

```sh
uname -a
cat /proc/cpuinfo
m5 exit                  # cleanly stops the gem5 simulation
```

`m5 exit` is gem5's special instruction. Back in the first terminal
gem5 stops and writes its final `m5out/stats.txt`.

## Why this is interesting

You just ran a real Linux kernel cycle-by-cycle on a simulated CPU.
Every memory access, every cache miss, every branch is in
`stats.txt`. Cross-reference any counter against the Linux boot log
to see what microarchitectural events the kernel triggered.
