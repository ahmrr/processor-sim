import sys
import argparse


from model import *
from utils import *


class Controller:
    def __init__(self, input_file: str, data_mem_size: int, step_mode=False):
        """Initialize a new controller"""

        # * Read in byte contents of input file
        with open(input_file, "rb") as file:
            data = file.read()

        # * Create a new model with specified instruction, data memory, and step mode
        self.model = Model(bytearray(data), bytearray(data_mem_size), step_mode)

    def control_loop(self):
        """Manages the global control loop"""

        # * Update model infinitely; view/model handle quitting
        while True:
            self.update_model()

    def update_model(self):
        """Updates the model every clock cycle based on some logic"""

        # * Run all pipeline stages
        self.model.run_IF()
        self.model.run_ID()
        self.model.run_EX()
        self.model.run_MEM()
        self.model.run_WB()

        # * Exit if no more instructions
        if self.model.state.pc >= len(self.model.state.inst_mem) - 4:
            self.model.state.run = False


if __name__ == "__main__":
    # * Parse input args
    parser = argparse.ArgumentParser(
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
        default=1024,
        metavar="size",
        type=int,
        help="specify custom size of data memory; default is 1024",
    )
    args = parser.parse_args()

    # * Initialize a new controller, set the step mode, and loop it
    controller = Controller(args.input_file[0], args.memory[0], args.step)
    controller.control_loop()
