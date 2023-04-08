from view import *
from utils import *
import typing

if __name__ == "__main__":
    print("\033[91;1merror:\033[0m wrong file; please run src/controller.py.")
    sys.exit(0)


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

    def run_IF(self, prev_pl_regs: State.pl_regs):
        """Run the Instruction Fetch stage"""

        # Pass PC to pipeline register
        self.state.pl_regs.IF_ID.pc = self.state.pc
        # Fetch instruction
        self.state.pl_regs.IF_ID.inst = fetch_inst(self.state.pc, self.state.inst_mem)

        # Update cycles
        self.state.cycles += 1

        # --> NEED TO IMPLEMENT JUMP STUFF HERE!!!! <--
        # If we want to branch and ALU result is 0, branch to PC + 4 + branch_addr
        if self.state.pl_regs.EX_MEM.cl.branch and self.state.pl_regs.EX_MEM.zero_flag:
            self.state.pc = self.state.pl_regs.EX_MEM.branch_addr
        # Otherwise, go to next instruction
        else:
            self.state.pc += 4

        # Update pipeline PC
        self.state.pl_regs.IF_ID.pc = self.state.pc

    def run_ID(self, prev_pl_regs: State.pl_regs):
        """Run the Instruction Decode stage"""

        # Pass PC ahead to next pipeline register
        self.state.pl_regs.ID_EX.pc = prev_pl_regs.IF_ID.pc

        # Determines control line values and passes them to the pipeline register
        self.state.pl_regs.ID_EX.cl = control(prev_pl_regs.IF_ID.inst)

        # Pass the potential write registers to the next pipeline register (FOR WRITE)
        self.state.pl_regs.ID_EX.reg_1 = (  # this is the register number of rd
            prev_pl_regs.IF_ID.inst & 0b000000_00000_00000_11111_00000_000000
        ) >> 11
        self.state.pl_regs.ID_EX.reg_2 = (  # this is the register number of rt
            prev_pl_regs.IF_ID.inst & 0b000000_00000_11111_00000_00000_000000
        ) >> 16

        # Read from registers, and pass the values (FOR ALU)
        self.state.pl_regs.ID_EX.data_1 = (
            self.state.regs[  # this is the value stored in rs
                (prev_pl_regs.IF_ID.inst & 0b000000_11111_00000_00000_00000_000000)
                >> 21
            ]
        )
        self.state.pl_regs.ID_EX.data_2 = (
            self.state.regs[  # this is the value stored in rt
                (prev_pl_regs.IF_ID.inst & 0b000000_00000_11111_00000_00000_000000)
                >> 16
            ]
        )

        # Parse the immediate value (FOR I-type)
        self.state.pl_regs.ID_EX.imm = twos_decode(
            prev_pl_regs.IF_ID.inst & 0b000000_00000_00000_11111_11111_111111, 16
        )

        # Parse the jump address (FOR j-type)
        self.state.pl_regs.ID_EX.jump_addr = (
            (prev_pl_regs.IF_ID.inst & 0b000000_11111_11111_11111_11111_111111) << 2
        ) + (prev_pl_regs.IF_ID.pc << 28)

    def run_EX(self, prev_pl_regs: State.pl_regs):
        """Run the ALU Execution stage"""

        # Passes the necessary control lines onto the next stage
        self.state.pl_regs.EX_MEM.cl.mem_to_reg = prev_pl_regs.ID_EX.cl.mem_to_reg
        self.state.pl_regs.EX_MEM.cl.reg_write = prev_pl_regs.ID_EX.cl.reg_write
        self.state.pl_regs.EX_MEM.cl.mem_read = prev_pl_regs.ID_EX.cl.mem_read
        self.state.pl_regs.EX_MEM.cl.mem_write = prev_pl_regs.ID_EX.cl.mem_write
        self.state.pl_regs.EX_MEM.cl.branch = prev_pl_regs.ID_EX.cl.branch
        self.state.pl_regs.EX_MEM.cl.jump = prev_pl_regs.ID_EX.cl.jump

        # The first ALU operand comes from the register file
        operand1 = prev_pl_regs.ID_EX.data_1
        # The second ALU operand comes from a mux, determined by the value of alu_src
        operand2 = (
            prev_pl_regs.ID_EX.imm
            if prev_pl_regs.ID_EX.cl.alu_src
            else prev_pl_regs.ID_EX.data_2
        )

        # ALU control unit (determines the value of the ALU control lines)
        if prev_pl_regs.ID_EX.cl.alu_op == 0b00:
            # lw or sw instruction
            alu_control = 0b0010
        elif prev_pl_regs.ID_EX.cl.alu_op == 0b01:
            # beq instruction
            alu_control = 0b0110
        elif prev_pl_regs.ID_EX.cl.alu_op == 0b10:
            # Need to look at the funct field
            funct = prev_pl_regs.ID_EX.imm & 0b000000_00000_00000_00000_00000_111111
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
            self.state.stats.alu_and_cnt += 1
        elif alu_control == 0b0001:
            # or
            self.state.pl_regs.EX_MEM.alu_result = operand1 | operand2
            self.state.stats.alu_or_cnt += 1
        elif alu_control == 0b0010:
            # add
            self.state.pl_regs.EX_MEM.alu_result = (operand1 + operand2) & 0xFFFFFFFF
            self.state.stats.alu_add_cnt += 1
        elif alu_control == 0b0110:
            # subtract
            self.state.pl_regs.EX_MEM.alu_result = (operand1 - operand2) & 0xFFFFFFFF
            self.state.stats.alu_sub_cnt += 1
            pass
        elif alu_control == 0b0111:
            # slt
            self.state.pl_regs.EX_MEM.alu_result = operand1 < operand2
            self.state.stats.alu_slt_cnt += 1
            pass

        # Determines the value of the zero flag
        self.state.pl_regs.EX_MEM.zero_flag = self.state.pl_regs.EX_MEM.alu_result == 0

        # Passes on the correct register to write to in the later WB stage
        self.state.pl_regs.EX_MEM.reg = (
            prev_pl_regs.ID_EX.reg_1
            if prev_pl_regs.ID_EX.cl.reg_dst
            else prev_pl_regs.ID_EX.reg_2
        )

        # Calculates the branch address
        self.state.pl_regs.EX_MEM.branch_addr = prev_pl_regs.ID_EX.pc + (
            prev_pl_regs.ID_EX.imm << 2
        )

        # Passes on data_2 in the case of a store word instruction
        self.state.pl_regs.EX_MEM.data = prev_pl_regs.ID_EX.data_2

        # Passes on the jump address
        self.state.pl_regs.EX_MEM.jump_addr = prev_pl_regs.EX_MEM.jump_addr

    def run_MEM(self, prev_pl_regs: State.pl_regs):
        """Run the Memory Access stage"""

        # Passes control line values to the next pipeline stage
        self.state.pl_regs.MEM_WB.cl.reg_write = prev_pl_regs.EX_MEM.cl.reg_write
        self.state.pl_regs.MEM_WB.cl.mem_to_reg = prev_pl_regs.EX_MEM.cl.mem_to_reg
        # Passes the ALU result and register to write to to the next pipeline stage
        self.state.pl_regs.MEM_WB.alu_result = prev_pl_regs.EX_MEM.alu_result
        self.state.pl_regs.MEM_WB.reg = prev_pl_regs.EX_MEM.reg

        # Reads from memory
        if prev_pl_regs.EX_MEM.cl.mem_read:
            self.state.pl_regs.MEM_WB.read_data = read_mem(
                prev_pl_regs.EX_MEM.alu_result, self.state.data_mem
            )
        # Writes to memory
        if prev_pl_regs.EX_MEM.cl.mem_write:
            write_mem(
                prev_pl_regs.EX_MEM.alu_result,
                prev_pl_regs.EX_MEM.data,
                self.state.data_mem,
            )

    def run_WB(self, prev_pl_regs: State.pl_regs):
        """Run the Write Back stage"""

        write_value = (
            prev_pl_regs.MEM_WB.read_data
            if prev_pl_regs.MEM_WB.cl.mem_to_reg
            else prev_pl_regs.MEM_WB.alu_result
        )

        if prev_pl_regs.MEM_WB.cl.reg_write:
            self.state.regs[prev_pl_regs.MEM_WB.reg] = write_value

        pass
