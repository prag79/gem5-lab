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

# Match any stat line whose path ends in `.numCycles` or `.committedInsts`,
# regardless of how the SimpleProcessor instance is laid out underneath
# `system.processor.*`. Different gem5 versions / multi-core configs use
# `cores.core`, `cores0.core`, `core`, etc. — being permissive here makes
# the script survive schema churn.
CYCLES_RE = re.compile(r"^(\S*\.numCycles)\s+(\d+)", re.MULTILINE)
INSTS_RE  = re.compile(r"^(\S*\.committedInsts)\s+(\d+)", re.MULTILINE)

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

    cycles_matches = CYCLES_RE.findall(stats)
    insts_matches  = INSTS_RE.findall(stats)
    if not (cycles_matches and insts_matches):
        # Surface a few likely candidate stats so the user can fix the
        # regex without having to grep stats.txt themselves.
        candidates = [
            line for line in stats.splitlines()
            if "Cycles" in line or "Inst" in line
        ][:20]
        raise RuntimeError(
            f"Could not find numCycles/committedInsts in {outdir}/stats.txt.\n"
            "Stat lines that mention Cycles or Inst (first 20):\n  "
            + "\n  ".join(candidates)
        )

    # If multiple cores reported, take the first (single-core lab) and
    # also print the path so the student can see exactly which stat we
    # used.
    cycles_path, cycles_str = cycles_matches[0]
    insts_path,  insts_str  = insts_matches[0]
    cycles = int(cycles_str)
    insts  = int(insts_str)
    print(f"  using {cycles_path} = {cycles}")
    print(f"  using {insts_path} = {insts}")
    results[name] = {
        "cycles": cycles,
        "insts":  insts,
        "cpi":    round(cycles / insts, 4),
    }

print("\n=== Summary ===")
print(json.dumps(results, indent=2))
