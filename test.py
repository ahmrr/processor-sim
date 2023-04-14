# import sys
# import curses

# screen = curses.initscr()
# screen.keypad(True)

# curses.noecho()
# curses.cbreak()
# curses.curs_set(False)
# if curses.has_colors():
#     curses.start_color()

# opt = "nothing, yet"

# while opt != "q":
#     screen.clear()
#     screen.addstr(0, 0, f"you entered {opt}")
#     screen.refresh()

#     opt = screen.getkey()


# curses.echo()
# curses.nocbreak()
# curses.curs_set(True)
# screen.keypad(False)
# curses.echo()
# curses.endwin()

# sys.exit(0)

# input("")

#!/usr/bin/env python

# import curses

# screen = curses.initscr()

# try:
#     screen.border(0)

#     box1 = curses.newwin(20, 20, 5, 5)
#     box1.box()

#     screen.refresh()
#     box1.refresh()

#     box1.addstr(1, 1, "hello")
#     box1.refresh()

#     screen.getch()

# finally:
#     curses.endwin()


# def twos_decode(num: int, bits: int):
#     """Converts a signed two's-complement number of specified length to a signed decimal integer"""

#     return num - (1 << bits) if num & 1 << (bits - 1) else num


# test = 0xFFFF

# print(f"num is {test:#020b}\nresult is {twos_decode(test, 16):#020b}")


# def split_chunks(string: str, size: int):
#     buff: list[str] = []
#     for i in range(0, len(string), size):
#         buff.append(string[i : i + size] if i + size < len(string) else string[i:])
#     return buff


# string = "12345678901234"
# print(f"string\t{string}\nsplit\t{split_chunks(string, 4)}")


# def print_bytes(data: bytearray):
#     data[0] = 100
#     print(data)


# data = bytearray(10)
# print(data)
# print_bytes(data)
# print(data)


# def write_mem(start: int, data: int, data_mem: bytearray):
#     data_mem[start : start + 4] = data.to_bytes(4, signed=True)


# data_mem = bytearray(10)
# start = 0
# data: int = -1
# print(data_mem)
# write_mem(start, data, data_mem)
# print(data_mem)

# print("IF/ID\tID/EX\tEX/MEM\tMEM/WB")

# with open("test/sample-data.dat", "wb") as file:
#     file.write(bytes.fromhex("00 00 00 01 00 00 00 0F"))


import typing
import sys


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


def decode_inst(inst: int) -> str:
    """Converts binary to a MIPS instruction"""

    inst_opcode = (inst & 0b111111_00000_00000_00000_00000_000000) >> 26
    inst_func = inst & 0b000000_00000_00000_00000_00000_111111

    # For nop
    decoded_inst = "nop"

    for key, val in instructions.items():
        if val["i_type"] == "R" and val["i_func"] == inst_func and inst_opcode == 0:
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


with open(sys.argv[1], "rb") as file:
    while True:
        inst = decode_inst(int.from_bytes(file.read(4)))
        if inst == "nop":
            break
        print(inst)
