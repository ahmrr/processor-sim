from utils import *

import sys
import curses


class View:
    def __init__(self, step_mode: bool):
        """Initialize a new view"""

        # * Create new curses screen
        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, -1, -1)

        self._create_win()

        # * Set the exception hook to first close curses and then print the exception, so that terminal isn't ruined
        def exc_hook(exctype, value, traceback):
            shutdown(self.screen)
            if issubclass(exctype, curses.error):
                print(tty.ERR + "error:" + tty.END + " terminal is too small")
                return
            sys.__excepthook__(exctype, value, traceback)

        sys.excepthook = exc_hook

        self.rerender = self._rerender_step if step_mode else self._rerender_jump

    def _rerender_step(self, state: State):
        """Rerender the view with prompt for user step input"""

        # data_mem = "".join(f"{byte:b}" for byte in state.inst_mem)
        # data_mem_split = split_chunks(data_mem, 32)

        # # * Clear screen and print state values
        # for i in range(8):
        #     self.data_mem_win.addstr(
        #         1 + i,
        #         2,
        #         data_mem_split[i],
        #     )

        # self.screen.clear()
        # self.stat_win.clear()
        self.stat_win.addstr(
            1, 2, "Stats", curses.A_BOLD | curses.A_ITALIC | curses.A_UNDERLINE
        )
        self.stat_win.addstr(3, 2, f"{state.pl_regs.IF_ID.inst:#034b}"[2:])
        self.stat_win.addstr(
            4,
            2,
            f"{decode_inst(state.pl_regs.IF_ID.inst):32}",
        )
        self.stat_win.addstr(6, 2, f"Cycles\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.cycles))
        self.stat_win.addstr(7, 2, f"Inst. count\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.stats.instruction_cnt))
        self.stat_win.addstr(8, 2, f"PC\t\t", curses.A_ITALIC)
        self.stat_win.addstr(str(state.pc))
        self._update_win()

        # * If there are more instructions left
        if state.run:
            # * Return if user enters step command (move to next instruction), otherwise break and shutdown
            self.screen.addstr(
                self.screen.getmaxyx()[0] - 1,
                2,
                f"{' Paused / (q)uit, (s)tep ':─<25}",
                curses.A_ITALIC,
            )
            while True:
                opt = self.screen.getkey()
                if opt == "q":
                    break
                elif opt == "s":
                    return
        # * If no more instructions left
        else:
            # * Discard input until user enters quit command
            self.screen.addstr(
                self.screen.getmaxyx()[0] - 1,
                2,
                f"{' Finish / (q)uit ':─<25}",
                curses.A_ITALIC,
            )
            while True:
                opt = self.screen.getkey()
                if opt == "q":
                    break

        # * Shutdown curses and exit
        shutdown(self.screen)
        sys.exit(0)

    def _rerender_jump(self, state: State):
        """Rerender the view without prompting for user step input"""

        # * Clear screen and print state values
        self.screen.clear()
        self.screen.addstr(0, 0, f"binary inst:\t{state.pl_regs.IF_ID.inst:#032b}")
        self.screen.addstr(1, 0, f"MIPS inst:\t{decode_inst(state.pl_regs.IF_ID.inst)}")
        self.screen.addstr(2, 0, f"cycles:\t\t{state.cycles}")
        self.screen.addstr(3, 0, f"pc:\t\t{state.pc}")

        # * Do nothing if there are more instructions left
        if state.run:
            return
        # * If no more instructions left
        else:
            # * Discard input until user enters quit command
            self.screen.addstr(8, 0, "FINISH / (q)uit")
            while self.screen.getkey() != "q":
                pass

        # * Shutdown curses and exit
        shutdown(self.screen)
        sys.exit(0)

    def _create_win(self):
        lines, cols = self.screen.getmaxyx()
        self.reg_win = curses.newwin(lines // 3, 3 * cols // 3, 0, 0)
        self.stat_win = curses.newwin(lines // 3, cols // 3, 0, 2 * cols // 3)
        self.pl_win = curses.newwin(lines // 3, cols // 2, lines // 3, 0)
        self.pl_reg_cl_win = curses.newwin(lines // 3, cols // 2, 2 * lines // 3, 0)
        self.data_mem_win = curses.newwin(
            2 * lines // 3, cols // 2, lines // 3, cols // 2
        )

        self.screen.refresh()

        self._update_win()

    def _update_win(self):
        self.reg_win.border(0, " ", 0, " ", 0, curses.ACS_HLINE, curses.ACS_VLINE, " ")
        self.reg_win.refresh()

        self.stat_win.border(0, 0, 0, " ", 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)
        self.stat_win.refresh()

        self.pl_win.border(0, " ", 0, " ", 0, curses.ACS_HLINE, curses.ACS_VLINE, " ")
        self.pl_win.refresh()

        self.pl_reg_cl_win.border(
            0, " ", 0, 0, 0, curses.ACS_HLINE, 0, curses.ACS_HLINE
        )
        self.pl_reg_cl_win.refresh()

        self.data_mem_win.box()
        self.data_mem_win.refresh()
