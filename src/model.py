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

    def run_IF(self, prev_state: State):
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

    def run_ID(self, prev_state: State):
        """Run the Instruction Decode stage"""

        # * Pass PC ahead to next pipeline register
        self.state.pl_regs.ID_EX.pc = self.state.pl_regs.IF_ID.pc
        # * Pass appropriate

        pass

    def run_EX(self, prev_state: State):
        """Run the ALU Execution stage"""

        # Passes the necessary control lines onto the next stage
        self.state.pl_regs.EX_MEM.cl.mem_to_reg = prev_state.pl_regs.ID_EX.cl.mem_to_reg
        self.state.pl_regs.EX_MEM.cl.reg_write = prev_state.pl_regs.ID_EX.cl.reg_write
        self.state.pl_regs.EX_MEM.cl.mem_read = prev_state.pl_regs.ID_EX.cl.mem_read
        self.state.pl_regs.EX_MEM.cl.mem_write = prev_state.pl_regs.ID_EX.cl.mem_write
        self.state.pl_regs.EX_MEM.cl.branch = prev_state.pl_regs.ID_EX.cl.branch

        # The first ALU operand comes from the register file
        operand1 = prev_state.pl_regs.ID_EX.data_1
        # The second ALU operand comes from a mux, determined by the value of
        # alu_src
        operand2 = (
            prev_state.pl_regs.ID_EX.imm
            if prev_state.pl_regs.ID_EX.cl.alu_src
            else prev_state.pl_regs.ID_EX.data_2
        )

        # ALU control unit (determines the value of the ALU control lines)
        if prev_state.pl_regs.ID_EX.cl.alu_op == 0b00:
            # lw or sw instruction
            alu_control = 0b0010
        elif prev_state.pl_regs.ID_EX.cl.alu_op == 0b01:
            # beq instruction
            alu_control = 0b0110
        elif prev_state.pl_regs.ID_EX.cl.alu_op == 0b10:
            # Need to look at the funct field
            funct = prev_state.pl_regs.ID_EX.imm & 0b111111
            if funct == 0b100000:
                # add instruction
                alu_control = 0b0010
            elif funct == 0b100010:
                # sub instruction
                alu_control = 0b0110
            elif funct == 0b100100:
                # and instruction
                alu_control = 0b0000
            elif funct == 0b100101:
                # or instruction
                alu_control = 0b0001
            elif funct == 0b101010:
                # slt instruction
                alu_control = 0b0111

        # Simulates ALU calculation
        if alu_control == 0b0000:
            # and
            self.state.pl_regs.EX_MEM.alu_result = operand1 & operand2
        elif alu_control == 0b0001:
            # or
            self.state.pl_regs.EX_MEM.alu_result = operand1 | operand2
        elif alu_control == 0b0010:
            # add
            self.state.pl_regs.EX_MEM.alu_result = (operand1 + operand2) & 0xFFFFFFFF
        elif alu_control == 0b0110:
            # subtract
            self.state.pl_regs.EX_MEM.alu_result = (operand1 - operand2) & 0xFFFFFFFF
            pass
        elif alu_control == 0b0111:
            # slt
            self.state.pl_regs.EX_MEM.alu_result = operand1 < operand2
            pass

        # Determines the value of the zero flag
        self.state.pl_regs.EX_MEM.zero_flag = self.state.pl_regs.EX_MEM.alu_result == 0

        # Passes on the correct register to write to in the later WB stage
        self.state.pl_regs.EX_MEM.reg = (
            prev_state.pl_regs.ID_EX.reg_1
            if prev_state.pl_regs.ID_EX.cl.reg_dst
            else prev_state.pl_regs.ID_EX.reg_2
        )

        # Calculates the branch address
        self.state.pl_regs.EX_MEM.branch_addr = prev_state.pl_regs.ID_EX.pc + (
            prev_state.pl_regs.ID_EX.imm << 2
        )

        # Passes on data_2 in the case of a store word instruction
        self.state.pl_regs.EX_MEM.data = prev_state.pl_regs.ID_EX.data_2

    def run_MEM(self, prev_state: State):
        """Run the Memory Access stage"""

        pass

    def run_WB(self, prev_state: State):
        """Run the Write Back stage"""

        pass
