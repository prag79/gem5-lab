"""Lab 03 - run the same SE-mode hello binary with two CPU models.

Prints a JSON summary of cycles, instructions, and CPI for each.
This is the headline gem5 demo: same binary, same memory, only the
CPU pipeline model changed - and the numbers move.

We invoke our local run-se.py against the locally-built hello-se.elf
instead of the gem5 example riscv-hello.py: that file doesn't exist in
gem5 v23.0.1.0, and even if it did, it would call obtain_resource(),
which crashes against the rebuilt gem5-resources service (HTTP 410).
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BINARY = HERE / "hello-se.elf"
RUN_SCRIPT = HERE / "run-se.py"

CASES = [
    ("atomic", "ATOMIC"),
    ("o3",     "O3"),
]

CYCLES_RE = re.compile(r"system\.processor\.cores\.core\.numCycles\s+(\d+)")
INSTS_RE  = re.compile(r"system\.processor\.cores\.core\.committedInsts\s+(\d+)")

if not BINARY.is_file():
    raise SystemExit(
        f"Missing {BINARY}. Run `make` in {HERE} first (the `lab 03` "
        "dispatcher does this automatically)."
    )

results = {}

for name, cpu in CASES:
    outdir = f"m5out-{name}"
    cmd = [
        "gem5-riscv",
        "--outdir", outdir,
        str(RUN_SCRIPT),
        str(BINARY),
        "--cpu-type", cpu,
    ]
    print(f"\n=== Running {name} ({cpu}) ===")
    subprocess.run(cmd, check=True)

    with open(f"{outdir}/stats.txt") as f:
        stats = f.read()

    cycles_match = CYCLES_RE.search(stats)
    insts_match  = INSTS_RE.search(stats)
    if not (cycles_match and insts_match):
        raise RuntimeError(
            f"Could not find numCycles/committedInsts in {outdir}/stats.txt; "
            "the gem5 stats schema may have changed for your version."
        )

    cycles = int(cycles_match.group(1))
    insts  = int(insts_match.group(1))
    results[name] = {
        "cycles": cycles,
        "insts":  insts,
        "cpi":    round(cycles / insts, 4),
    }

print("\n=== Summary ===")
print(json.dumps(results, indent=2))
