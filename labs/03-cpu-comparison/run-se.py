"""Lab 03 - SE-mode runner parameterized by CPU model.

Mirrors lab 01's run-se.py but takes --cpu-type so compare.py can run
the same binary across multiple CPU models. We do not use
obtain_resource() here: the gem5-resources metadata service no longer
responds to v23.0.1.0 clients, so any reliance on it crashes at startup.
"""
import argparse

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator

CPU_TYPE_MAP = {
    "ATOMIC": CPUTypes.ATOMIC,
    "TIMING": CPUTypes.TIMING,
    "O3": CPUTypes.O3,
    "MINOR": CPUTypes.MINOR,
}

parser = argparse.ArgumentParser()
parser.add_argument("binary", help="Static RV64 ELF to run")
parser.add_argument(
    "--cpu-type",
    default="ATOMIC",
    choices=sorted(CPU_TYPE_MAP),
    help="gem5 stdlib CPU model to use",
)
args = parser.parse_args()

board = SimpleBoard(
    clk_freq="1GHz",
    processor=SimpleProcessor(
        cpu_type=CPU_TYPE_MAP[args.cpu_type],
        isa=ISA.RISCV,
        num_cores=1,
    ),
    memory=SingleChannelDDR3_1600("64MiB"),
    cache_hierarchy=NoCache(),
)
board.set_se_binary_workload(BinaryResource(local_path=args.binary))
Simulator(board=board).run()
