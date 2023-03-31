from view import *
from utils import *
import typing


class Model:
    def __init__(
        self,
        observer_function: typing.Callable,
        instruction_memory: bytes,
        data_memory_size: int,
    ):
        """Initialize a new model

        observer_function: function - a function to call when model is updated
        """

        self.state = State()
        # self.state.data_memory = bytes(data_memory_size)
        self.view = View()
        self.observer_function = observer_function

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
