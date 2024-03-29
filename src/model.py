from view import *
from utils import *

# * Print error if this file is attempted to run
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

        # If we are bubbling, run a nop
        if self.state.bubbles:
            self.state.pl_regs.IF_ID.pc = self.state.pc
            self.state.pl_regs.IF_ID.inst = 0x00000000
            self.state.bubbles -= 1

        else:
            # If we want to branch and ALU result is 0, branch to PC + 4 + branch_addr
            if prev_pl_regs.EX_MEM.cl.branch and prev_pl_regs.EX_MEM.zero_flag:
                self.state.pc = prev_pl_regs.EX_MEM.branch_addr

            # If we want to jump, set pc to the jump address
            if prev_pl_regs.EX_MEM.cl.jump:
                self.state.pc = prev_pl_regs.EX_MEM.jump_addr

            # Fetch instruction
            self.state.pl_regs.IF_ID.inst = fetch_inst(
                self.state.pc, self.state.inst_mem
            )

            # Update instruction count
            self.state.stats.instruction_cnt += 1

            # Go to next instruction
            self.state.pc += 4

            # Update pipeline PC
            self.state.pl_regs.IF_ID.pc = self.state.pc

        # Update cycles
        self.state.cycles += 1

    def run_ID(self, prev_pl_regs: State.pl_regs):
        """Run the Instruction Decode stage"""

        # Checks for data hazard
        self.state.bubbles = max(self.is_data_hazard(prev_pl_regs), self.state.bubbles)
        # If there is a data hazard, insert a nop and move pc back to the correct address
        if self.state.bubbles and prev_pl_regs.IF_ID.inst != 0x00000000:
            # Insert a nop for the current instruction
            prev_pl_regs.IF_ID.inst = 0x00000000
            # Move pc back to the current instruction
            prev_pl_regs.IF_ID.pc -= 4
            self.state.pc = prev_pl_regs.IF_ID.pc
            # Decrement the number of bubbles left
            self.state.bubbles -= 1
            # Remove the current instruction from the instruction count
            self.state.stats.instruction_cnt -= 1

        # Checks for control hazard
        self.state.bubbles = max(
            self.is_control_hazard(prev_pl_regs), self.state.bubbles
        )

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

        # Read from the registers, and pass on the values
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
            prev_pl_regs.IF_ID.inst & 0b000000_11111_11111_11111_11111_111111
        )

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
            else:
                # nop instruction
                alu_control = None

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
        elif alu_control == 0b0111:
            # slt
            self.state.pl_regs.EX_MEM.alu_result = operand1 < operand2
            self.state.stats.alu_slt_cnt += 1

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

        # Calculates the jump address
        self.state.pl_regs.EX_MEM.jump_addr = (
            prev_pl_regs.ID_EX.pc & 0b11111000_00000000_00000000_00000000
        ) + (prev_pl_regs.ID_EX.jump_addr << 2)

        # Passes on data_2 in the case of a store word instruction
        self.state.pl_regs.EX_MEM.data = prev_pl_regs.ID_EX.data_2

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
            self.state.stats.mem_reads += 1

        # Writes to memory
        if prev_pl_regs.EX_MEM.cl.mem_write:
            write_mem(
                prev_pl_regs.EX_MEM.alu_result,
                prev_pl_regs.EX_MEM.data,
                self.state.data_mem,
            )
            self.state.stats.mem_writes += 1

    def run_WB(self, prev_pl_regs: State.pl_regs):
        """Run the Write Back stage"""

        write_value = (
            prev_pl_regs.MEM_WB.read_data
            if prev_pl_regs.MEM_WB.cl.mem_to_reg
            else prev_pl_regs.MEM_WB.alu_result
        )

        if prev_pl_regs.MEM_WB.cl.reg_write:
            self.state.regs[prev_pl_regs.MEM_WB.reg] = write_value

    def is_data_hazard(self, prev_pl_regs: State.pl_regs) -> int:
        """Checks for data hazards, returns the number of bubbles needed to
        resolve the hazard"""

        IF_ID_rs = (
            prev_pl_regs.IF_ID.inst & 0b000000_11111_00000_00000_00000_000000
        ) >> 21

        IF_ID_rt = (
            prev_pl_regs.IF_ID.inst & 0b000000_00000_11111_00000_00000_000000
        ) >> 16

        EX_MEM_rd = prev_pl_regs.EX_MEM.reg
        MEM_WB_rd = prev_pl_regs.MEM_WB.reg
        ID_EX_rt = prev_pl_regs.ID_EX.reg_2

        if EX_MEM_rd == IF_ID_rs and prev_pl_regs.EX_MEM.cl.reg_write:
            return 2
        elif EX_MEM_rd == IF_ID_rt and prev_pl_regs.EX_MEM.cl.reg_write:
            return 2
        elif MEM_WB_rd == IF_ID_rs and prev_pl_regs.MEM_WB.cl.reg_write:
            return 1
        elif MEM_WB_rd == IF_ID_rt and prev_pl_regs.MEM_WB.cl.reg_write:
            return 1
        elif ID_EX_rt == IF_ID_rs and prev_pl_regs.ID_EX.cl.mem_read:
            return 2
        elif ID_EX_rt == IF_ID_rt and prev_pl_regs.ID_EX.cl.mem_read:
            return 2
        else:
            return 0

    def is_control_hazard(self, prev_pl_regs: State.pl_regs) -> int:
        """Checks for data hazards, returns the number of bubbles needed to
        resolve the hazard"""

        # If the instruction is beq or j, stall until pc is updated
        op = (prev_pl_regs.IF_ID.inst & 0b111111_00000_00000_00000_00000_000000) >> 26
        if op == 0b000100 or op == 0b000010:
            return 1
        else:
            return 0
