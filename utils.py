import sys
import typing

if __name__ == "__main__":
    sys.exit(0)


class State:
    """ Represents the state of the processor

        registers: typing.Annotated[list[int], 32] - 32 32-bit MIPS registers
    """

    registers: typing.Annotated[list[int], 32]


class tty:
    """Stores ANSI color codes
    """

    END = '\033[0m'
    BLD = '\033[1m'
    WRN = '\033[95m'
    ERR = '\033[91;1m'
    INF = '\033[94m'
