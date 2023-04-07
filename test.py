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

print("IF/ID\tID/EX\tEX/MEM\tMEM/WB")