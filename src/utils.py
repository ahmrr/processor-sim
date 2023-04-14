import sys
import typing
import curses

# * Print error if this file is attempted to run
if __name__ == "__main__":
    print("\033[91;1merror:\033[0m wrong file; please run src/controller.py.")
    sys.exit(0)


class State:
    """Represents the state of the processor

    `cycles: int` - the total cycle count; whenever this is updated, the observer function is called

    `stats: types.SimpleNamespace` - the general statistics of the processor
        `mem_reads: int` - the total number of memory reads
        `mem_writes: int` - the total number of memory writes
        `alu_add_cnt: int` - the total number of ALU add instructions
        `alu_sub_cnt: int` - the total number of ALU sub instructions
        `alu_and_cnt: int` - the total number of ALU and instructions
        `alu_or_cnt: int` - the total number of ALU or instructions
        `alu_slt_cnt: int` - the total number of ALU slt (set less-than) instructions

    `pc: int` - the current program counter
    `regs: list[int]` - the values of each of the 32 registers

    `bubbles: int` - the number of bubbles to run

    `pl_regs: class` - stores information of each of the pipeline registers
        `IF_ID: class` - the pipeline register between the IF and ID stages
            `pc: int` - the original PC + 4, forwarded to the EX stage (if needed for branch instruction)
            `inst: int` - the raw data instruction, not decoded
        `ID_EX: class` - the pipeline register between the ID and EX stages
            `pc: int` - the original PC + 4, forwarded to the EX stage (if needed for branch instruction)
            `data_1` - the first value read from the register file
            `data_2` - the second value read from the register file
            `reg_1: int` - the first register operand specified in the instruction, if available
            `reg_2: int` - the second register operand specified in the instruction, if available
            `imm: int` - the value stored in the immediate field in the instruction, if available
            `jump_addr: int` - the value stored in the address field in the instruction, if available
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)
                `mem_read: bool` - whether memory read access is needed for this instruction (1) or not (0)
                `mem_write: bool` - whether memory write access is needed for this instruction (1) or not (0)
                `reg_dst: bool` - whether the register destination number comes from from the rd field (1) or rt field (0)
                `branch: bool` - whether the current instruction is a branch instruction
                `jump: bool` - whether the current instruction is a jump instruction
                `alu_src: bool` - whether the second ALU operand comes from the sign-extended immediate in the instruction (1) or from the register file (0)
                `alu_op: int` - the funct of the ALU operation to do (if applicable)
        `EX_MEM: class` - the pipeline register between the EX and MEM stages
            `branch_addr: int` - the calculated branch target address, if the current instruction is branch
            `jump_addr: int` - the value stored in the address field in the instruction, if available
            `zero_flag: bool` - whether the ALU subtraction resulted in a 0 (if slt, bne, or be instruction)
            `alu_result: int` - the result of the ALU operation
            `data: int` - the value read from the register file to store into memory (sw)
            `reg: int` - the register to write to
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)
                `mem_read: bool` - whether memory read access is needed for this instruction (1) or not (0)
                `mem_write: bool` - whether memory write access is needed for this instruction (1) or not (0)
                `branch: bool` - whether the current instruction is a branch instruction
                `jump: bool` - whether the current instruction is a jump instruction
        `MEM_WB: class` - the pipeline register between the MEM and WB stages
            `alu_result: int` - the result of the ALU operation
            `read_data: bool` - the data read from memory (if applicable), for lw instructions
            `reg: int` - the register to write to
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)

    `data_mem: bytes` - the data memory bytes buffer
    `inst_mem: bytes` - the instruction memory (input file) bytes buffer

    `run: Bool` - whether to continue running the program
    `step_mode: Bool` - the mode in which to run the program; True = in steps, False = all at once
    `observer_function: typing.Callable` - function to call whenever cycles is updated
    """

    pl_stage_inst: list[int] = [0, 0, 0, 0, 0]

    _cycles = 0

    @property
    def cycles(self):
        return self._cycles

    @cycles.setter
    def cycles(self, value):
        self._cycles = value
        self.observer_function(self)

    @cycles.deleter
    def cycles(self):
        del self._cycles

    class stats:
        mem_reads = 0
        mem_writes = 0
        alu_add_cnt = 0
        alu_sub_cnt = 0
        alu_and_cnt = 0
        alu_or_cnt = 0
        alu_slt_cnt = 0
        instruction_cnt = 0

    pc = 0
    regs = [0] * 32

    bubbles = 0

    class pl_regs:
        class IF_ID:
            pc = 0
            inst = 0

        class ID_EX:
            pc = 0
            data_1 = 0
            data_2 = 0
            reg_1 = 0
            reg_2 = 0
            imm = 0
            jump_addr = 0

            class cl:
                mem_to_reg = False
                reg_write = False
                mem_read = False
                mem_write = False
                reg_dst = False
                branch = False
                jump = False
                alu_src = False
                alu_op = 0b10

        class EX_MEM:
            branch_addr = 0
            jump_addr = 0
            zero_flag = False
            alu_result = 0
            data = 0
            reg = 0

            class cl:
                mem_to_reg = False
                reg_write = False
                mem_read = False
                mem_write = False
                branch = False
                jump = False

        class MEM_WB:
            alu_result = 0
            read_data = 0
            reg = 0

            class cl:
                mem_to_reg = False
                reg_write = False

    data_mem: bytearray
    inst_mem: bytearray

    run = True
    step_mode = False
    observer_function: typing.Callable = None


class tty:
    """Stores program-used ANSI escape codes"""

    END = "\033[0m"
    BLD = "\033[1m"
    WRN = "\033[95m"
    ERR = "\033[91;1m"
    INF = "\033[94m"


def fetch_inst(pc: int, inst_mem: bytearray) -> int:
    """Fetch an instruction from instruction memory
    `pc: int` - the PC (byte offset) to fetch instruction at
    `inst_mem: bytearray` - the instruction memory to fetch instruction from

    `return: int` - the fetched instruction, or `nop`/0 if out of bounds
    """

    # * If we are still inside inst_mem, fetch and return the instruction
    if pc < len(inst_mem):
        return int.from_bytes(inst_mem[pc : pc + 4])
    # * Otherwise, the requested address is out of bounds; return nop
    else:
        return 0


def write_mem(start: int, data: int, data_mem: bytearray):
    """Write a specific amount of bytes to data memory
    `start: int` - the starting position to insert at
    `data: int` - the data (always 4 bytes)
    `data_mem: bytearray` - the data memory to insert in
    """

    data_mem[start : start + 4] = data.to_bytes(4, signed=True)


def read_mem(start: int, data_mem: bytearray) -> int:
    """Read a specific amount of bytes from data memory
    `start: int` - the starting position to read at
    `data_mem: bytearray` - the data memory to read from

    `return: int` - the value read from memory
    """

    return int.from_bytes(data_mem[start : start + 4], signed=True)


def decode_inst(inst: int) -> str:
    """Converts binary to a MIPS instruction
    `inst: int` - the instruction to decode

    `return: str` - the decoded instruction
    """

    # * Read opcode and possible funct field
    inst_opcode = (inst & 0b111111_00000_00000_00000_00000_000000) >> 26
    inst_func = inst & 0b000000_00000_00000_00000_00000_111111

    # * Initialize to nop
    decoded_inst = "nop"

    # * Iterate over keys and values in all possible instructions
    for key, val in instructions.items():
        # * If R-type instruction matched
        if val["i_type"] == "R" and val["i_func"] == inst_func and inst_opcode == 0:
            # * Read register numbers
            inst_rs = (inst & 0b000000_11111_00000_00000_00000_000000) >> 21
            inst_rt = (inst & 0b000000_00000_11111_00000_00000_000000) >> 16
            inst_rd = (inst & 0b000000_00000_00000_11111_00000_000000) >> 11

            # * Assemble decoded instruction
            decoded_inst = f"{key} ${inst_rd}, ${inst_rs}, ${inst_rt}"
        # * If I-type instruction matched
        elif val["i_type"] == "I" and val["i_opcode"] == inst_opcode:
            # * Read register numbers and immediate value
            inst_rs = (inst & 0b000000_11111_00000_00000_00000_000000) >> 21
            inst_rt = (inst & 0b000000_00000_11111_00000_00000_000000) >> 16
            inst_imm = inst & 0b000000_00000_00000_11111_11111_111111

            # * Convert unsigned immediate to two's-complement signed integer
            if inst_imm & 0b000000_00000_00000_10000_00000_000000:
                inst_imm = inst_imm - 0b000000_00000_00001_00000_00000_000000

            # * If lw or sw, assemble the decoded instruction
            if val["i_ops"] == 2:
                decoded_inst = f"{key} ${inst_rt}, {inst_imm}(${inst_rs})"
            # * If beq, assemble the decoded instruction
            elif val["i_ops"] == 3:
                decoded_inst = f"{key} ${inst_rs}, ${inst_rt}, {inst_imm}"
        # * If J-type instruction matched
        elif val["i_type"] == "J" and val["i_opcode"] == inst_opcode:
            # * Read address value
            inst_addr = inst & 0b000000_11111_11111_11111_11111_111111

            # * Convert unsigned address to two's-complement signed integer
            if inst_addr & 0b000000_10000_00000_00000_00000_000000:
                inst_addr = inst_addr - 0b000001_00000_00000_00000_00000_000000

            # * Assemble the decoded instruction
            decoded_inst = f"{key} {inst_addr}"

    return decoded_inst


def shutdown(screen: curses.window):
    """Resets terminal and shuts down a curses screen
    `screen: curses.window` - the screen to shut down
    """

    curses.echo()
    curses.nocbreak()
    curses.curs_set(True)
    screen.keypad(False)
    curses.endwin()


def control(inst: int) -> State.pl_regs.ID_EX.cl:
    """Returns control line values for an instruction ins
    `inst: int` - the instruction to return values for

    `return: State.pl_regs.ID_EX.cl` - the control lines corresponding to the instruction
    """

    cl = State.pl_regs.ID_EX.cl

    # * If instruction is nop
    if inst == 0x00000000:
        cl.reg_dst = False
        cl.alu_op = 0b10
        cl.alu_src = False
        cl.branch = False

        cl.mem_read = False
        cl.mem_write = False
        cl.reg_write = False
        cl.mem_to_reg = False
        cl.jump = False
        return cl

    # * Read instruction opcode
    op = (inst & 0b111111_00000_00000_00000_00000_000000) >> 26

    # * If instruction is R-type
    if op == 0b000000:
        cl.reg_dst = True
        cl.alu_op = 0b10
        cl.alu_src = False
        cl.branch = False

        cl.mem_read = False
        cl.mem_write = False
        cl.reg_write = True
        cl.mem_to_reg = False
        cl.jump = False
    # * If instruction is lw
    elif op == 0b100011:
        cl.reg_dst = False
        cl.alu_op = 0b00
        cl.alu_src = True
        cl.branch = False
        cl.mem_read = True
        cl.mem_write = False
        cl.reg_write = True
        cl.mem_to_reg = True
        cl.jump = False
    # * If instruction is sw
    elif op == 0b101011:
        cl.reg_dst = False
        cl.alu_op = 0b00
        cl.alu_src = True
        cl.branch = False
        cl.mem_read = False
        cl.mem_write = True
        cl.reg_write = False
        cl.mem_to_reg = False
        cl.jump = False
    # * If instruction is beq
    elif op == 0b000100:
        cl.reg_dst = False
        cl.alu_op = 0b01
        cl.alu_src = False
        cl.branch = True
        cl.mem_read = False
        cl.mem_write = False
        cl.reg_write = False
        cl.mem_to_reg = False
        cl.jump = False
    # * If instruction is j
    elif op == 0b000010:
        cl.reg_dst = False
        cl.alu_op = 0b10
        cl.alu_src = False
        cl.branch = False

        cl.mem_read = False
        cl.mem_write = False
        cl.reg_write = False
        cl.mem_to_reg = False
        cl.jump = True

    return cl


def twos_decode(num: int, bits: int) -> int:
    """Converts a signed two's-complement number of specified length to a signed decimal integer
    `num: int` - the number to convert
    `bits: int` - the size of the number (including sign bit)

    `return: int` - the signed two's-complement integer
    """

    return num - (1 << bits) if num & 1 << (bits - 1) else num


def split_chunks(string: str, size: int) -> list[str]:
    """Splits a string into chunks of a specific size
    `string: str` - the string to split
    `size: int` - the size of each chunk

    `return: list[str]` - the list containing chunked strings
    """

    return [string[i : i + size] for i in range(0, len(string), size)]


def clear_block(win: curses.window, start_y: int, start_x: int, end_y: int, end_x: int):
    """Clear a specific block in a curses window
    `win: curses.window` - the window to clear
    `start_y: int` - the starting y value
    `start_x: int` - the starting x value
    `end_y: int` - the ending y value
    `end_x: int` - the ending x value
    """

    # * Add spaces over the entire interval
    for y in range(start_y, end_y):
        win.addstr(y, start_x, " " * (end_x - start_x))


def clear_win(win: curses.window):
    """Clear a curses window, taking into consideration a 1-wide inner border
    `win: curses.window` - the window to clear
    """

    # * Add spaces over the entire window
    for y in range(1, win.getmaxyx()[0] - 1):
        win.addstr(y, 2, " " * (win.getmaxyx()[1] - 3))


class Instruction(typing.TypedDict):
    """Stores a single instruction type

    `i_opcode: int` - the opcode of the instruction
    `i_type: typing.Literal["I", "R", "J"]` - the type of instruction; either R, I, or J
    `i_func: typing.NotRequired[int]` - the funct field of the instruction; not required
    `i_ops: int` - the number of operands (space-separated values) the instruction takes
    """

    i_opcode: int
    i_type: typing.Literal["I", "R", "J"]
    i_func: typing.NotRequired[int]
    i_ops: int


# * The four pipeline registers
PL_REGS: list[str] = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]

# * All implemented instructions
instructions: dict[str, Instruction] = {
    "lw": {"i_opcode": 0b100011, "i_type": "I", "i_ops": 2},
    "sw": {"i_opcode": 0b101011, "i_type": "I", "i_ops": 2},
    "beq": {"i_opcode": 0b000100, "i_type": "I", "i_ops": 3},
    "add": {"i_opcode": 0b000000, "i_type": "R", "i_ops": 3, "i_func": 0b100000},
    "sub": {"i_opcode": 0b000000, "i_type": "R", "i_ops": 3, "i_func": 0b100010},
    "and": {"i_opcode": 0b000000, "i_type": "R", "i_ops": 3, "i_func": 0b100100},
    "or": {"i_opcode": 0b000000, "i_type": "R", "i_ops": 3, "i_func": 0b100101},
    "slt": {"i_opcode": 0b000000, "i_type": "R", "i_ops": 3, "i_func": 0b101010},
    "j": {"i_opcode": 0b000010, "i_type": "J", "i_ops": 1},
}
