from view import *
from utils import *
import typing


class Model:
    def __init__(
        self,
        instruction_memory: bytes,
        data_memory_size: int,
    ):
        """Initialize a new model, with specified instruction memory (input file) and data memory size"""

        self.state = State()
        print(data_memory_size)
        self.state.data_memory = bytearray(data_memory_size)
        self.view = View()
        self.observer_function = self.view.rerender

    def changed(self):
        """Must be called whenever a value (or multiple values) are modified in this model's state"""

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
