import sys
import getopt

from model import *
from utils import *


class Controller:
    def __init__(self, input_file: str, data_memory_size: int, step_mode: bool):
        with open(input_file, "rb") as file:
            data: bytes = file.read()

        self.model = Model(
            instruction_memory=data,
            data_memory_size=data_memory_size,
        )
        self.step = step_mode
        self.run = True

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
                print("----------------------------", end="")

    def update_model(self):
        """Updates the model every clock cycle based on some logic"""

        self.model.state.stats.cycles += 1
        self.model.changed()


if __name__ == "__main__":
    # Get command-line options; if any invalid options are present, error
    try:
        options = getopt.getopt(sys.argv[1:], "hsm:", ["help", "step", "memory"])
    except getopt.GetoptError as err:
        print(tty.ERR + "error: " + tty.END + err.msg)
        sys.exit(1)

    # print(f"argv is {sys.argv[1:]}\nopt is {options}")

    # If no arguments are specified at all, or only flags are specified, error
    if len(options[1]) == 0:
        print(tty.ERR + "error: " + tty.END + "input file not specified")
        sys.exit(1)
    # If multiple possible input files (args without hyphens) are specified, error
    if len(options[1]) > 1:
        print(tty.ERR + "error: " + tty.END + " multiple possible input files")
        sys.exit(1)

    data_memory_size = 1024
    step = False

    for opt, arg in options[0]:
        if opt in ("-h", "--help"):
            print("usage: python3 controller.py [FLAGS] [INPUT FILE]")
            sys.exit(0)
        elif opt in ("-s", "--step"):
            step = True
        elif opt in ("-m", "--memory"):
            data_memory_size = arg

    file_name = options[1][0]

    # print(f"file {file_name}\nopts {options}")

    controller = Controller(file_name, data_memory_size, step)
    controller.control_loop()
