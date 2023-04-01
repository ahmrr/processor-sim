from view import *
from utils import *
import typing


class Model:
    def __init__(
        self,
        inst_memory: bytearray,
        data_memory: bytearray,
    ):
        """Initialize a new model, with specified instruction memory (input file) and data memory size"""

        self.state = State()
        print(f"inst_memory:\t{len(inst_memory)} bytes")
        print(f"data_memory:\t{len(data_memory)} bytes")
        self.state.inst_mem = inst_memory
        self.state.data_mem = data_memory

        self.view = View()
        self.observer_function = self.view.rerender

    def changed(self):
        """Must be called whenever a value (or multiple values) are modified in this model's state"""

        print(f"binary inst:\t{fetch_inst(self.state.pc, self.state.inst_mem):#032b}")
        print(
            f"MIPS inst:\t{decode_inst(fetch_inst(self.state.pc, self.state.inst_mem))}"
        )

        self.observer_function(self.state)

    def run_IF(self):
        """Run the Instruction Fetch stage"""

        pass

    def run_ID(self):
        """Run the Instruction Decode stage"""

        pass

    def run_EX(self):
        """Run the ALU Execution stage"""

        pass

    def run_MEM(self):
        """Run the Memory Access stage"""

        pass

    def run_WB(self):
        """Run the Write Back stage"""

        pass
