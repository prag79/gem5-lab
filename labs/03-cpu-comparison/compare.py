"""Lab 03 - run the same SE-mode hello binary with two CPU models.

Prints a JSON summary of cycles, instructions, and CPI for each.
This is the headline gem5 demo: same binary, same memory, only the
CPU pipeline model changed - and the numbers move.
"""
import json
import re
import subprocess

CASES = [
    ("atomic", "ATOMIC"),
    ("o3",     "O3"),
]

CYCLES_RE = re.compile(r"system\.processor\.cores\.core\.numCycles\s+(\d+)")
INSTS_RE  = re.compile(r"system\.processor\.cores\.core\.committedInsts\s+(\d+)")

results = {}

for name, cpu in CASES:
    outdir = f"m5out-{name}"
    cmd = [
        "gem5-riscv",
        "--outdir", outdir,
        "/opt/gem5/configs/example/gem5_library/riscv-hello.py",
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
