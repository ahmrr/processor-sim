import sys
import getopt

from model import *
from utils import *


class Controller:
    def __init__(self, input_file: str, data_memory_size: int, step_mode: bool):
        with open(input_file, "rb") as file:
            data: bytes = file.read()

        self.model = Model(
            observer_function=self.view.rerender,
            instruction_memory=data,
            data_memory_size=data_memory_size,
        )
        self.step = step_mode
        self.run = True

        print(f"data memory size is {len(self.model.state.data_memory)}\n")

    def control_loop(self):
        if self.step:
            while self.run:
                self.update_model()
        else:
            while self.run:
                self.update_model()

    def update_model(self):
        pass


if __name__ == "__main__":
    # Get command-line options; if any invalid options are present, error
    try:
        options = getopt.getopt(sys.argv[1:], "hsm:", ["help", "step", "memory"])
    except getopt.GetoptError as err:
        print(tty.ERR + "error: " + tty.END + err.msg)
        sys.exit(1)

    print(f"argv is {sys.argv[1:]}\nopt is {options}")

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
            pass
        elif opt in ("-s", "--step"):
            pass
        elif opt in ("-m", "--memory"):
            pass

    file_name = options[1][0]

    print(f"file {file_name}\nopts {options}")

    controller = Controller(file_name, data_memory_size, step)
    # controller.control_loop()
