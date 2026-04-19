"""Lab 02 - boot Linux on a simulated RISC-V HiFive board (FS mode).

This is a local replacement for `/opt/gem5/configs/example/gem5_library/
riscv-fs.py`. The shipped script calls `obtain_resource("riscv-bootloader-
vmlinux-5.10")` etc., which talks to the gem5-resources metadata service.
That service was rebuilt after gem5 v23.0.1.0 and now returns HTTP 410 for
old clients, so the example crashes on startup. We sidestep the whole
metadata layer by feeding gem5 the artifacts directly via local paths.

The Makefile next to this script downloads `bootloader-vmlinux-5.10` and
`riscv-disk.img` (gunzipped from `riscv-disk.img.gz`) from dist.gem5.org
on first run.
"""
from pathlib import Path

from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource, DiskImageResource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

requires(isa_required=ISA.RISCV)

HERE = Path(__file__).resolve().parent
KERNEL = HERE / "bootloader-vmlinux-5.10"
DISK = HERE / "riscv-disk.img"

for f in (KERNEL, DISK):
    if not f.is_file():
        raise SystemExit(
            f"Missing FS artifact: {f}\n"
            f"Run `make artifacts` in {HERE} first (the `lab 02` "
            "dispatcher does this automatically)."
        )

board = RiscvBoard(
    clk_freq="1GHz",
    processor=SimpleProcessor(
        cpu_type=CPUTypes.TIMING, isa=ISA.RISCV, num_cores=1
    ),
    memory=SingleChannelDDR3_1600(),
    cache_hierarchy=PrivateL1PrivateL2CacheHierarchy(
        l1d_size="32KiB", l1i_size="32KiB", l2_size="512KiB"
    ),
)

board.set_kernel_disk_workload(
    kernel=BinaryResource(local_path=str(KERNEL)),
    disk_image=DiskImageResource(local_path=str(DISK)),
)

print("Beginning simulation!")
Simulator(board=board).run()
