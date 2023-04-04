from view import *
from utils import *
import typing


class Model:
    def __init__(self, inst_memory: bytearray, data_memory: bytearray, step_mode=False):
        """Initialize a new model, with specified instruction memory (input file) and data memory size"""

        self.state = State()
        self.view = View(step_mode)
        self.state.observer_function = self.view.rerender
        self.state.inst_mem = inst_memory
        self.state.data_mem = data_memory
        # print(f"inst_memory:\t{len(self.state.inst_mem)} bytes")
        # print(f"data_memory:\t{len(self.state.data_mem)} bytes")

    def run_IF(self):
        """Run the Instruction Fetch stage"""

        # * Pass PC to pipeline register
        self.state.pl_regs.IF_ID.pc = self.state.pc
        # * Fetch instruction
        self.state.pl_regs.IF_ID.inst = fetch_inst(self.state.pc, self.state.inst_mem)

        # * Update cycles
        self.state.cycles += 1

        # * If we want to branch and ALU result is 0, branch to PC + 4 + branch_addr
        if self.state.pl_regs.EX_MEM.cl.branch and self.state.pl_regs.EX_MEM.zero_flag:
            self.state.pc += 4 + self.state.pl_regs.EX_MEM.branch_addr
        # * Otherwise, go to next instruction
        else:
            self.state.pc += 4

        # * Update pipeline PC
        self.state.pl_regs.IF_ID.pc = self.state.pc

    def run_ID(self):
        """Run the Instruction Decode stage"""

        # * Pass PC ahead to next pipeline register
        self.state.pl_regs.ID_EX.pc = self.state.pl_regs.IF_ID.pc
        # * Pass appropriate

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
