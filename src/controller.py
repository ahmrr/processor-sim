import sys
import argparse


from model import *
from utils import *


class Controller:
    def __init__(self, input_file: str, data_memory_size: int, step_mode: bool):
        with open(input_file, "rb") as file:
            data = file.read()

        print("----------------------------")

        self.model = Model(bytearray(data), bytearray(data_memory_size))
        self.step = step_mode
        self.run = True

        print(f"step:\t\t{step_mode}")

    def control_loop(self):
        """Manages the global control loop"""

        print("----------------------------")

        # Call update_model, either in steps or continuously
        if self.step:
            while self.run:
                self.update_model()
                print("----------------------------", end="")
                try:
                    input("")
                except KeyboardInterrupt:
                    sys.exit(0)
        else:
            while self.run:
                self.update_model()
                print("----------------------------")

        print("program execution finished")
        print("----------------------------")

    def update_model(self):
        """Updates the model every clock cycle based on some logic"""

        self.model.changed()

        self.model.state.stats.cycles += 1
        self.model.state.pc += 4

        if self.model.state.pc >= len(self.model.state.inst_mem):
            self.run = False


if __name__ == "__main__":
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

    controller = Controller(args.input_file[0], args.memory[0], args.step)
    controller.control_loop()
