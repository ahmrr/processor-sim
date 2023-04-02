from utils import *


class View:
    def __init__(self):
        """Initialize a new view"""

        pass

    def rerender(self, state: State):
        """Rerender the view"""

        print(f"binary inst:\t{state.pl_regs.IF_ID.inst:#032b}")
        print(f"MIPS inst:\t{decode_inst(state.pl_regs.IF_ID.inst)}")
        print(f"cycles:\t\t{state.cycles}")
        print(f"pc:\t\t{state.pc}")
