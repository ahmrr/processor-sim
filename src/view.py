from utils import *

import sys
import curses

# For macos
# curses.A_ITALIC = curses.A_BOLD

if __name__ == "__main__":
    print("\033[91;1merror:\033[0m wrong file; please run src/controller.py.")
    sys.exit(0)


class View:
    def __init__(self, step_mode: bool):
        """Initialize a new view"""

        # Create new curses screen
        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, -1, -1)
            # curses.init_pair(2, curses.COLOR_BLUE, -1)

        self._create_win()

        # Set the exception hook to first close curses and then print the exception, so that terminal isn't ruined
        def exc_hook(exctype, value, traceback):
            shutdown(self.screen)
            if issubclass(exctype, curses.error):
                print(tty.ERR + "error:" + tty.END + " terminal is too small")
                sys.exit(1)
            sys.__excepthook__(exctype, value, traceback)

        sys.excepthook = exc_hook

        self.rerender = self._rerender_step if step_mode else self._rerender_jump

        self.pl_stage = 0
        self.data_mem_start = 0

    def _disp_reg_win(self, state: State):
        clear_win(self.reg_win)
        self.reg_win.addstr(
            1, 2, "Registers", curses.A_BOLD | curses.A_ITALIC | curses.A_UNDERLINE
        )
        for i in range(32):
            self.reg_win.addstr(
                3 + (i % 8),
                2 + (i // 8) * 13,
                f"{f'${i}':>{3 if i >= 8 else 2}}",
                curses.A_ITALIC,
            )
            self.reg_win.addstr(" " + f"{state.regs[i]:#010x}"[2:])

        self.reg_win.addstr(12, 2, f"PC ", curses.A_ITALIC)
        self.reg_win.addstr(f"{state.pc:#010x}"[2:])

    def _disp_stat_win(self, state: State):
        clear_win(self.stat_win)
        self.stat_win.addstr(
            1, 2, "Stats", curses.A_BOLD | curses.A_ITALIC | curses.A_UNDERLINE
        )
        self.stat_win.addstr(3, 2, "Binary inst.\t", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.pl_regs.IF_ID.inst:#034b}"[2:])
        self.stat_win.addstr(4, 2, "MIPS inst.\t", curses.A_ITALIC)
        self.stat_win.addstr(f"{decode_inst(state.pl_regs.IF_ID.inst):32}")
        self.stat_win.addstr(6, 2, f"Cycles\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.cycles))
        self.stat_win.addstr("\tALU adds   ", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.stats.alu_add_cnt}")
        self.stat_win.addstr(", subs   ", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.stats.alu_sub_cnt}")
        self.stat_win.addstr(7, 2, f"Inst. count\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.stats.instruction_cnt))
        self.stat_win.addstr("\tALU ands   ", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.stats.alu_and_cnt}")
        self.stat_win.addstr(8, 2, f"Mem. reads\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.stats.mem_reads))
        self.stat_win.addstr("\tALU ors    ", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.stats.alu_or_cnt}")
        self.stat_win.addstr(9, 2, f"Mem. writes\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.stats.mem_writes))
        self.stat_win.addstr("\tALU slts   ", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.stats.alu_slt_cnt}")
        self.stat_win.addstr(10, 2, f"Bubbles left\t", curses.A_ITALIC)
        self.stat_win.addstr(f"{state.bubbles}")

    def _disp_pl_info_win(self, state: State, pl_reg: str):
        clear_win(self.pl_info_win)

        self.pl_info_win.addstr(
            1,
            2,
            "Pipeline Info",
            curses.A_BOLD | curses.A_ITALIC | curses.A_UNDERLINE,
        )

        match pl_reg:
            case "IF/ID":
                self.pl_info_win.addstr(
                    3, 2, "IF/ID register", curses.A_ITALIC | curses.A_BOLD
                )
                self.pl_info_win.addstr(4, 2, f"PC\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.IF_ID.pc:#010x}")
                self.pl_info_win.addstr(5, 2, f"Inst.\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.IF_ID.inst:#010x}")
            case "ID/EX":
                self.pl_info_win.addstr(
                    3,
                    2,
                    "ID/EX register\t\tID/EX control lines",
                    curses.A_ITALIC | curses.A_BOLD,
                )
                self.pl_info_win.addstr(4, 2, f"PC\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.pc:#010x}")
                self.pl_info_win.addstr(5, 2, f"Reg 1 data\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.data_1:#010x}")
                self.pl_info_win.addstr(6, 2, f"Reg 2 data\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.data_2:#010x}")
                self.pl_info_win.addstr(7, 2, f"Reg 1 #\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.reg_1:#07b}")
                self.pl_info_win.addstr(8, 2, f"Reg 2 #\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.reg_2:#07b}")
                self.pl_info_win.addstr(9, 2, f"Immediate\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.imm:#010x}")
                self.pl_info_win.addstr(10, 2, f"Jump addr.\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.ID_EX.jump_addr:#010x}")

                self.pl_info_win.addstr(4, 32, f"Mem to reg\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.mem_to_reg)))
                self.pl_info_win.addstr(5, 32, f"Reg write\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.reg_write)))
                self.pl_info_win.addstr(6, 32, f"Mem read\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.mem_read)))
                self.pl_info_win.addstr(7, 32, f"Mem write\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.mem_write)))
                self.pl_info_win.addstr(8, 32, f"Reg dest.\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.reg_dst)))
                self.pl_info_win.addstr(9, 32, f"Branch\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.branch)))
                self.pl_info_win.addstr(10, 32, f"Jump\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.jump)))
                self.pl_info_win.addstr(11, 32, f"ALU src\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.ID_EX.cl.alu_src)))
                self.pl_info_win.addstr(12, 32, f"ALU op\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(f"{state.pl_regs.ID_EX.cl.alu_op:#02b}"))
            case "EX/MEM":
                self.pl_info_win.addstr(
                    3,
                    2,
                    "EX/MEM register\t\tEX/MEM control lines",
                    curses.A_ITALIC | curses.A_BOLD,
                )
                self.pl_info_win.addstr(4, 2, f"Branch addr.\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.EX_MEM.branch_addr:#010x}")
                self.pl_info_win.addstr(5, 2, f"Jump addr.\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.EX_MEM.jump_addr:#010x}")
                self.pl_info_win.addstr(6, 2, f"Zero flag\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.zero_flag)))
                self.pl_info_win.addstr(7, 2, f"ALU result\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.EX_MEM.alu_result:#010x}")
                self.pl_info_win.addstr(8, 2, f"Reg data\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.EX_MEM.data:#010x}")
                self.pl_info_win.addstr(8, 2, f"Dest. reg #\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.EX_MEM.reg:#010x}")

                self.pl_info_win.addstr(4, 32, f"Mem to reg\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.mem_to_reg)))
                self.pl_info_win.addstr(5, 32, f"Reg write\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.reg_write)))
                self.pl_info_win.addstr(6, 32, f"Mem read\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.mem_read)))
                self.pl_info_win.addstr(7, 32, f"Mem write\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.mem_write)))
                self.pl_info_win.addstr(8, 32, f"Branch\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.branch)))
                self.pl_info_win.addstr(9, 32, f"Jump\t\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.EX_MEM.cl.jump)))

            case "MEM/WB":
                self.pl_info_win.addstr(
                    3,
                    2,
                    "MEM/WB register\t\tMEM/WB control lines",
                    curses.A_ITALIC | curses.A_BOLD,
                )
                self.pl_info_win.addstr(4, 2, f"ALU result\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.MEM_WB.alu_result:#010x}")
                self.pl_info_win.addstr(5, 2, f"Read data\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.MEM_WB.read_data:#010x}")
                self.pl_info_win.addstr(6, 2, f"Dest. reg #\t", curses.A_ITALIC)
                self.pl_info_win.addstr(f"{state.pl_regs.MEM_WB.reg:#010x}")

                self.pl_info_win.addstr(4, 32, f"Mem to reg\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.MEM_WB.cl.mem_to_reg)))
                self.pl_info_win.addstr(5, 32, f"Reg write\t", curses.A_ITALIC)
                self.pl_info_win.addstr(str(int(state.pl_regs.MEM_WB.cl.reg_write)))

        self.pl_info_win.addstr(
            self.pl_info_win.getmaxyx()[0] - 2,
            1,
            " <left>: prev. reg, <right>: next reg ",
            curses.A_ITALIC,
        )

    def _disp_data_mem_win(self, state: State, start: int):
        clear_win(self.data_mem_win)
        self.data_mem_win.addstr(
            1,
            2,
            "Data Memory",
            curses.A_BOLD | curses.A_ITALIC | curses.A_UNDERLINE,
        )

        fmt = 6 if len(state.data_mem) <= 0x10000 else 10

        for i in range(
            0,
            min(
                16 * (self.data_mem_win.getmaxyx()[0] - 6), len(state.data_mem) - start
            ),
            16,
        ):
            self.data_mem_win.addstr(3 + i // 16, 2, f"{(start + i):#0{fmt}x}: "[2:])
            for j in range(0, 16, 4):
                self.data_mem_win.addstr(
                    f"{state.data_mem[start + i + j : start + i + j + 4].hex()} "
                )

        self.data_mem_win.addstr(
            self.data_mem_win.getmaxyx()[0] - 2,
            1,
            " <up>: prev. frame, <down>: next frame ",
            curses.A_ITALIC,
        )

    def _rerender_step(self, state: State):
        """Rerender the view with prompt for user input"""

        self._disp_reg_win(state)
        self.reg_win.refresh()

        self._disp_stat_win(state)
        self.stat_win.refresh()

        self._disp_data_mem_win(state, self.data_mem_start)
        self.data_mem_win.refresh()

        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
        self.pl_info_win.refresh()

        # If there are more instructions left
        if state.run:
            # Return if user enters step command (move to next instruction), otherwise break and shutdown
            self.data_mem_win.addstr(
                self.data_mem_win.getmaxyx()[0] - 1,
                2,
                f"{' Paused'}",
                curses.A_BOLD,
            )
            self.data_mem_win.addstr(f"{'; q: quit, s: step ':─<21}", curses.A_ITALIC)
            self.data_mem_win.refresh()
            while True:
                match self.screen.getkey():
                    case "q":
                        break
                    case "s":
                        return
                    case "KEY_RIGHT":
                        self.pl_stage = (self.pl_stage + 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_LEFT":
                        self.pl_stage = (self.pl_stage - 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_UP":
                        if (
                            self.data_mem_start
                            - 16 * (self.data_mem_win.getmaxyx()[0] - 6)
                            >= 0
                        ):
                            self.data_mem_start -= 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                    case "KEY_DOWN":
                        if self.data_mem_start + 16 * (
                            self.data_mem_win.getmaxyx()[0] - 6
                        ) < len(state.data_mem):
                            self.data_mem_start += 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
        # If no more instructions left
        else:
            # Discard input until user enters quit command
            self.data_mem_win.addstr(
                self.data_mem_win.getmaxyx()[0] - 1,
                2,
                f"{' Done'}",
                curses.A_BOLD,
            )
            self.data_mem_win.addstr(f"{'; q: quit ':─<21}", curses.A_ITALIC)
            self.data_mem_win.refresh()
            while True:
                match self.screen.getkey():
                    case "q":
                        break
                    case "KEY_RIGHT":
                        self.pl_stage = (self.pl_stage + 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_LEFT":
                        self.pl_stage = (self.pl_stage - 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_UP":
                        if (
                            self.data_mem_start
                            - 16 * (self.data_mem_win.getmaxyx()[0] - 6)
                            >= 0
                        ):
                            self.data_mem_start -= 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                    case "KEY_DOWN":
                        if self.data_mem_start + 16 * (
                            self.data_mem_win.getmaxyx()[0] - 6
                        ) < len(state.data_mem):
                            self.data_mem_start += 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()

        # Shutdown curses and exit
        shutdown(self.screen)
        sys.exit(0)

    def _rerender_jump(self, state: State):
        """Rerender the view without prompting for user step input"""

        self._disp_reg_win(state)
        self.reg_win.refresh()

        self._disp_stat_win(state)
        self.stat_win.refresh()

        self._disp_data_mem_win(state, self.data_mem_start)
        self.data_mem_win.refresh()

        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
        self.pl_info_win.refresh()

        # Do nothing if there are more instructions left
        if state.run:
            return
        # If no more instructions left
        else:
            # Discard input until user enters quit command
            self.data_mem_win.addstr(
                self.data_mem_win.getmaxyx()[0] - 1,
                2,
                f"{' Done'}",
                curses.A_BOLD,
            )
            self.data_mem_win.addstr(f"{'; q: quit ':─<21}", curses.A_ITALIC)
            self.data_mem_win.refresh()
            while True:
                match self.screen.getkey():
                    case "q":
                        break
                    case "KEY_RIGHT":
                        self.pl_stage = (self.pl_stage + 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_LEFT":
                        self.pl_stage = (self.pl_stage - 1) % 4
                        self._disp_pl_info_win(state, pl_registers[self.pl_stage])
                        self.pl_info_win.refresh()
                    case "KEY_UP":
                        if (
                            self.data_mem_start
                            - 16 * (self.data_mem_win.getmaxyx()[0] - 6)
                            >= 0
                        ):
                            self.data_mem_start -= 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()
                    case "KEY_DOWN":
                        if self.data_mem_start + 16 * (
                            self.data_mem_win.getmaxyx()[0] - 6
                        ) < len(state.data_mem):
                            self.data_mem_start += 16 * (
                                self.data_mem_win.getmaxyx()[0] - 6
                            )
                        self._disp_data_mem_win(state, self.data_mem_start)
                        self.data_mem_win.refresh()

        # Shutdown curses and exit
        shutdown(self.screen)
        sys.exit(0)

    def _create_win(self):
        lines, cols = self.screen.getmaxyx()

        reg_win_dim = (14, cols // 2)
        stat_win_dim = (12, cols // 2)
        data_win_dim = (lines - reg_win_dim[0], cols // 2)
        pl_info_win_dim = (lines - stat_win_dim[0], cols // 2)

        self.reg_win = curses.newwin(reg_win_dim[0], reg_win_dim[1], 0, 0)
        self.stat_win = curses.newwin(
            stat_win_dim[0], stat_win_dim[1], 0, reg_win_dim[1]
        )
        # self.pl_win = curses.newwin(lines // 3, cols // 2, lines // 3, 0)
        self.data_mem_win = curses.newwin(
            data_win_dim[0], data_win_dim[1], reg_win_dim[0], 0
        )
        self.pl_info_win = curses.newwin(
            pl_info_win_dim[0], pl_info_win_dim[1], stat_win_dim[0], data_win_dim[1]
        )

        self.screen.refresh()

        self.reg_win.border(0, " ", 0, " ", 0, curses.ACS_HLINE, curses.ACS_VLINE, " ")
        self.reg_win.refresh()

        self.stat_win.border(0, 0, 0, " ", 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)
        self.stat_win.refresh()

        # self.pl_win.border(0, " ", 0, " ", 0, curses.ACS_HLINE, curses.ACS_VLINE, " ")
        # self.pl_win.refresh()

        self.data_mem_win.border(0, " ", 0, 0, 0, curses.ACS_HLINE, 0, curses.ACS_HLINE)
        self.data_mem_win.refresh()

        self.pl_info_win.box()
        self.pl_info_win.refresh()
