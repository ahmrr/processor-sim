import sys
from collections.abc import Callable
import typing

if __name__ == "__main__":
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

    `pl_regs: class` - stores information of each of the pipeline registers
        `IF_ID: class` - the pipeline register between the IF and ID stages
            `pc: int` - the original PC + 4, forwarded to the EX stage (if needed for branch instruction)
            `inst: int` - the raw data instruction, not decoded
        `ID_EX: class` - the pipeline register between the ID and EX stages
            `pc: int` - the original PC + 4, forwarded to the EX stage (if needed for branch instruction)
            `reg_1: int` - the value stored in the first register operand specified in the instruction, if available
            `reg_2: int` - the value stored in the second register operand specified in the instruction, if available
            `imm: int` - the value stored in the immediate field in the instruction, if available
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)
                `mem_read: bool` - whether memory read access is needed for this instruction (1) or not (0)
                `mem_write: bool` - whether memory write access is needed for this instruction (1) or not (0)
                `reg_dst: bool` - whether the register destination number comes from from the rd field (1) or rt field (0)
                `branch: bool` - whether the current instruction is a branch instruction
                `alu_src: bool` - whether the second ALU operand comes from the sign-extended immediate in the instruction (1) or from the register file (0)
                `alu_op: int` - the funct of the ALU operation to do (if applicable)
        `EX_MEM: class` - the pipeline register between the EX and MEM stages
            `branch_addr: int` - the calculated branch target address, if the current instruction is branch
            `zero_flag: bool` - whether the ALU subtraction resulted in a 0 (if slt, bne, or be instruction)
            `alu_result: int` - the result of the ALU operation
            `reg_2: int` - the second register value, in case the instruction is a sw instruction
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)
                `mem_read: bool` - whether memory read access is needed for this instruction (1) or not (0)
                `mem_write: bool` - whether memory write access is needed for this instruction (1) or not (0)
                `branch: bool` - whether the current instruction is a branch instruction
        `MEM_WB: class` - the pipeline register between the MEM and WB stages
            `alu_result: int` - the result of the ALU operation
            `read_data: bool` - the data read from memory (if applicable), for lw instructions
            `cl: class` - the control lines (and ALU operation/funct) set for this stage
                `mem_to_reg: bool` - whether to source register write-back output from memory (1) or ALU result (0)
                `reg_write: bool` - whether to write to a register (1) or do nothing (0)
    `data_mem: bytes` - the data memory bytes buffer
    `inst_mem: bytes` - the instruction memory (input file) bytes buffer
    """

    def __init__(self, observer_function: Callable) -> None:
        self.observer_function = observer_function

    _cycles = 0

    @property
    def cycles(self):
        return self._cycles

    @cycles.setter
    def cycles(self, value):
        self.observer_function(self)
        self._cycles = value

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

    pc = 0
    regs = [0] * 32

    class pl_regs:
        class IF_ID:
            pc = 0
            inst = 0

        class ID_EX:
            pc = 0
            reg_1 = 0
            reg_2 = 0
            imm = 0

            class cl:
                mem_to_reg = False
                reg_write = False
                mem_read = False
                mem_write = False
                reg_dst = False
                branch = False
                alu_src = False
                alu_op = 0

        class EX_MEM:
            branch_addr = 0
            zero_flag = False
            alu_result = 0
            reg_2 = 0

            class cl:
                mem_to_reg = False
                reg_write = False
                mem_read = False
                mem_write = False
                branch = False

        class MEM_WB:
            alu_result = 0
            read_data = 0

            class cl:
                mem_to_reg = False
                reg_write = False

    # * Data memory (size TBD by user/default size is 1024B)
    data_mem: bytearray
    # * Instruction memory (size TBD by user's input file)
    inst_mem: bytearray
    # * Control lines
    # control_lines = types.SimpleNamespace(
    #     {
    #         "reg_write": False,
    #         "mem_read": False,
    #         "mem_write": False,
    #         "reg_read": False,
    #     }
    # )


class tty:
    """Stores ANSI color codes"""

    END = "\033[0m"
    BLD = "\033[1m"
    WRN = "\033[95m"
    ERR = "\033[91;1m"
    INF = "\033[94m"


def fetch_inst(pc: int, inst_mem: bytearray) -> int:
    return int.from_bytes(inst_mem[pc : pc + 4])


def decode_inst(inst: int) -> str:
    """Converts binary to a MIPS instruction"""

    inst_opcode = (inst & 0b111111_00000_00000_00000_00000_000000) >> 26
    inst_func = inst & 0b000000_00000_00000_00000_00000_111111

    for key, val in instructions.items():
        if val["i_type"] == "R" and val["i_func"] == inst_func:
            inst_rs = (inst & 0b000000_11111_00000_00000_00000_000000) >> 21
            inst_rt = (inst & 0b000000_00000_11111_00000_00000_000000) >> 16
            inst_rd = (inst & 0b000000_00000_00000_11111_00000_000000) >> 11

            decoded_inst = f"{key} ${inst_rd}, ${inst_rs}, ${inst_rt}"
        elif val["i_type"] == "I" and val["i_opcode"] == inst_opcode:
            inst_rs = (inst & 0b000000_11111_00000_00000_00000_000000) >> 21
            inst_rt = (inst & 0b000000_00000_11111_00000_00000_000000) >> 16
            inst_imm = inst & 0b000000_00000_00000_11111_11111_111111

            if inst_imm & 0b000000_00000_00000_10000_00000_000000:
                inst_imm = inst_imm - 0b000000_00000_00001_00000_00000_000000

            if val["i_ops"] == 2:
                decoded_inst = f"{key} ${inst_rt}, {inst_imm}(${inst_rs})"
            elif val["i_ops"] == 3:
                decoded_inst = f"{key} ${inst_rs}, ${inst_rt}, {inst_imm}"
        elif val["i_type"] == "J" and val["i_opcode"] == inst_opcode:
            inst_addr = inst & 0b000000_11111_11111_11111_11111_111111

            if inst_addr & 0b000000_10000_00000_00000_00000_000000:
                inst_addr = inst_addr - 0b000001_00000_00000_00000_00000_000000

            decoded_inst = f"{key} {inst_addr}"

    return decoded_inst


def data_hazard(inst_1: int, inst_2: int) -> bool:
    """Checks if two instructions have a RAW data hazard"""

    # * Get information of each instruction based on opcode/func field(s)
    for key, val in instructions.items():
        if (
            val["i_type"] == "R"
            and val["i_func"] == inst_1 & 0b000000_00000_00000_00000_00000_111111
            or val["i_opcode"]
            == (inst_1 & 0b111111_00000_00000_00000_00000_000000) >> 26
        ):
            inst_1_name = key
            inst_1_info = val
        if (
            val["i_type"] == "R"
            and val["i_func"] == inst_2 & 0b000000_00000_00000_00000_00000_111111
            or val["i_opcode"]
            == (inst_2 & 0b111111_00000_00000_00000_00000_000000) >> 26
        ):
            inst_2_name = key
            inst_2_info = val

    # * No data hazards with J-type instructions
    if inst_1_info["i_type"] == "J" or inst_2_info["i_type"] == "J":
        return False
    # * If one instruction is R-type and the other is I-type
    elif inst_1_info["i_type"] == "R" and inst_2_info["i_type"] == "I":
        # inst_1_rs = (inst_1 & 0b000000_11111_00000_00000_00000_000000) >> 21
        # inst_1_rt = (inst_1 & 0b000000_00000_11111_00000_00000_000000) >> 16
        inst_1_rd = (inst_1 & 0b000000_00000_00000_11111_00000_000000) >> 11

        inst_2_rs = (inst_2 & 0b000000_11111_00000_00000_00000_000000) >> 21
        inst_2_rt = (inst_2 & 0b000000_00000_11111_00000_00000_000000) >> 16

        # * Load or store op
        if inst_1_info["i_ops"] == 2:
            return inst_1_rd == inst_2_rs
        # * Other I-type op
        else:
            return inst_1_rd == inst_2_rs or inst_1_rd == inst_2_rt
    # * If one instruction is I-type and the other is R-type
    elif inst_1_info["i_type"] == "I" and inst_2_info["i_type"] == "R":
        return False
    # * If both instructions are I-type
    elif inst_1_info["i_type"] == "I" and inst_2_info["i_type"] == "I":
        # inst_1_rs = (inst_2 & 0b000000_11111_00000_00000_00000_000000) >> 21
        inst_1_rt = (inst_2 & 0b000000_00000_11111_00000_00000_000000) >> 16

        inst_2_rs = (inst_2 & 0b000000_11111_00000_00000_00000_000000) >> 21
        inst_2_rt = (inst_2 & 0b000000_00000_11111_00000_00000_000000) >> 16

        # * First instruction is load, second is load/store op
        if inst_1_name == "lw" and inst_2_info["i_ops"] == 2:
            return inst_1_rt == inst_2_rs
        # * First instruction is load, second is some other I-type op
        elif inst_1_name == "lw" and inst_2_info["i_ops"] == 3:
            return inst_1_rt == inst_2_rs or inst_1_rt == inst_2_rt
        # * First instruction is some other I-type op
        else:
            return False
    # * If both instructions are R-type
    elif inst_1_info["i_type"] == "R" and inst_2_info["i_type"] == "R":
        # inst_1_rs = (inst_1 & 0b000000_11111_00000_00000_00000_000000) >> 21
        # inst_1_rt = (inst_1 & 0b000000_00000_11111_00000_00000_000000) >> 16
        inst_1_rd = (inst_1 & 0b000000_00000_00000_11111_00000_000000) >> 11

        inst_2_rs = (inst_1 & 0b000000_11111_00000_00000_00000_000000) >> 21
        inst_2_rt = (inst_1 & 0b000000_00000_11111_00000_00000_000000) >> 16
        # inst_2_rd = (inst_1 & 0b000000_00000_00000_11111_00000_000000) >> 11

        return inst_1_rd == inst_2_rs or inst_1_rd == inst_2_rt

    return False


class Instruction(typing.TypedDict):
    i_opcode: int
    i_type: typing.Literal["I", "R", "J"]
    i_func: typing.NotRequired[int]
    i_ops: int


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
