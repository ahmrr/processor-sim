import sys
import typing

if __name__ == "__main__":
    sys.exit(0)


class State:
    """Represents the state of the processor

    registers: typing.Annotated[list[int], 32] - 32 32-bit MIPS registers
    """

    stats: dict[str, int] = {
        "cycle_count": 0,
        "mem_read_count": 0,
        "mem_write_count": 0,
        "alu_add_count": 0,
        "alu_sub_count": 0,
        "alu_and_count": 0,
        "alu_or_count": 0,
        "alu_slt_count": 0,
    }

    # Program counter
    pc: int
    # 32 32-bit registers
    registers: typing.Annotated[list[int], 32]
    # Pipeline register before ID stage
    pipeline_register_ID: dict[str, int] = {"pc": 0, "instruction": 0}
    # Pipeline register before EX stage
    pipeline_register_EX: dict[str, int] = {
        "pc": 0,
        "reg1": 0,
        "reg2": 0,
        "imm": 0,
        "ctrl_mem_to_reg": False,
        "ctrl_reg_write": False,
        "ctrl_mem_read": False,
        "ctrl_mem_write": False,
        "ctrl_reg_dst": False,
        "ctrl_branch": False,
        "ctrl_alu_src": False,
        "ctrl_alu_op": 0,
    }
    # Pipeline register before MEM stage
    pipeline_register_MEM: dict[str, int] = {
        "branch_pc": 0,
        "zero_flag": 0,
        "alu_result": 0,
        "reg2": 0,
        "ctrl_mem_to_reg": False,
        "ctrl_reg_write": False,
        "ctrl_mem_read": False,
        "ctrl_mem_write": False,
        "ctrl_branch": False,
    }
    # Pipeline register before WB stage
    pipeline_register_WB: dict[str, int] = {
        "alu_result": 0,
        "read_data": 0,
        "ctrl_mem_to_reg": False,
        "ctrl_reg_write": False,
    }
    # Data memory (size TBD by user/default size is 1024B)
    data_memory: bytes
    # Instruction memory (size TBD by user's input file)
    instruction_memory: bytes
    # Control lines
    control_lines: dict[str, bool] = {
        "reg_write": False,
        "mem_read": False,
        "mem_write": False,
        "reg_read": False,
    }


class tty:
    """Stores ANSI color codes"""

    END = "\033[0m"
    BLD = "\033[1m"
    WRN = "\033[95m"
    ERR = "\033[91;1m"
    INF = "\033[94m"
