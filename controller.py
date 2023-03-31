import sys
import getopt

from view import *
from model import *
from utils import *


class Controller():
    def __init__(self):
        self.view = View()
        self.model = Model(observer_function=self.view.rerender)
        self.run = True

    def control_loop(self):
        while (self.run):
            self.update_model()

    def update_model(self):
        pass


if __name__ == '__main__':
    # Get command-line options; if any invalid options are present, error
    try:
        options = getopt.getopt(sys.argv[1:], 'hs', ['help', 'step'])
    except getopt.GetoptError as err:
        print(tty.ERR + 'error: ' + tty.END + err.msg)
        sys.exit(1)

    print(f'argv is {sys.argv[1:]}\nopt is {options}')

    if "--help" in options[0] or "-h" in options[0]:
        print("""
        """)

    # If no arguments are specified at all, or only flags are specified, error
    if len(options[1]) == 0:
        print(tty.ERR + 'error: ' + tty.END + 'input file not specified')
        sys.exit(1)
    # If multiple possible input files (args without hyphens) are specified, error
    if len(options[1]) > 1:
        print(tty.ERR + 'error: ' + tty.END + ' multiple possible input files')
        sys.exit(1)

    file_name = options[1]

    print(f'file {file_name}\nopts {options}')

    # controller = Controller()
