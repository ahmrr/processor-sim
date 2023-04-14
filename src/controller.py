import sys
import argparse

from importlib.util import find_spec
from platform import system

# * Print error if curses doesn't exist
if find_spec("_curses") is None:
    print(
        "\033[91;1merror:\033[0m curses module not found; curses is needed to run this program."
    )
    if system() == "Windows":
        print('For \033[1mWindows\033[0m, run "python -m pip install windows-curses"')
    sys.exit(1)


from model import *
from utils import *


class Controller:
    def __init__(
        self,
        input_inst_mem: str,
        input_data_mem: str,
        data_mem_size: int,
        step_mode: bool = False,
    ):
        """Initialize a new controller

        `input_inst_mem: str` - the input instruction memory file
        `input_data_mem: str` - the input data memory file; if not available, then ""
        `data_mem_size: int` - the data memory size; if file is specified and smaller than given data memory, fill remaining space
        `step_mode: bool` - whether or not to step; default is False
        """

        # * Create data memory of given size
        data_mem = bytearray(data_mem_size)

        # * Read in byte contents of input instruction file
        with open(input_inst_mem, "rb") as file:
            inst_mem = file.read()
        # * If a data memory file is given, insert it into or replace data_mem
        if input_data_mem != "":
            with open(input_data_mem, "rb") as file:
                input_data = file.read()
                data_mem[: len(input_data)] = bytearray(input_data)

        # * Create a new Model with specified instruction, data memory, and step mode
        self.model = Model(bytearray(inst_mem), data_mem, step_mode)

    def control_loop(self):
        """Manages the global control loop"""

        # * Update model infinitely; view and/or model handle quitting
        while True:
            self.update_model()

    def update_model(self):
        """Updates the model every clock cycle, based on standard behavior of the MIPS 5-stage pipeline"""

        prev_pl_regs = self.model.state.pl_regs.__new__(self.model.state.pl_regs)

        # * Run all pipeline stages in correct order
        self.model.run_WB(prev_pl_regs)
        self.model.run_MEM(prev_pl_regs)
        self.model.run_EX(prev_pl_regs)
        self.model.run_ID(prev_pl_regs)
        self.model.run_IF(prev_pl_regs)

        # * Exit if no more instructions
        if self.model.state.pc >= len(self.model.state.inst_mem) + 12:
            self.model.state.run = False


if __name__ == "__main__":

    class ArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_help(sys.stderr)
            self.exit(22, tty.ERR + "error:" + tty.END + f" {message}\n")

    # * Parse input arguments
    parser = ArgumentParser(
        description="Simulate a MIPS-ISA 5-stage pipelined processor"
    )
    parser.add_argument(
        "input_file",
        metavar="infile",
        type=str,
        nargs=1,
        help="the input file (instruction memory)",
    )
    parser.add_argument(
        "-s",
        "--step",
        dest="step",
        action="store_const",
        const=True,
        default=False,
        help="enable stepping mode; wait for user input before beginning next clock cycle",
    )
    parser.add_argument(
        "-m",
        "--memory",
        "--mem",
        nargs=1,
        default=[1024],
        metavar="size",
        type=int,
        help="specify custom size of data memory; default is 1024",
    )
    parser.add_argument(
        "-d",
        "--data",
        nargs=1,
        default=[""],
        metavar="data",
        type=str,
        help="specify custom data memory input; default is empty. If a memory size is also specified, any remaining space not included in the input data file will be filled.",
    )
    args = parser.parse_args()

    # * Initialize a new controller, set the step mode, and loop it
    controller = Controller(args.input_file[0], args.data[0], args.memory[0], args.step)
    controller.control_loop()
