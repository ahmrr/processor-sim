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

        # * Set the exception hook to first close curses and then print the exception, so that terminal isn't ruined
        def exc_hook(exctype, value, traceback):
            shutdown(self.screen)
            sys.__excepthook__(exctype, value, traceback)

        sys.excepthook = exc_hook

        self.rerender = self._rerender_step if step_mode else self._rerender_jump

    def _rerender_step(self, state: State):
        """Rerender the view with prompt for user step input"""

        # * Clear screen and print state values
        self.screen.clear()
        self.screen.addstr(0, 0, f"binary inst:\t{state.pl_regs.IF_ID.inst:#032b}")
        self.screen.addstr(1, 0, f"MIPS inst:\t{decode_inst(state.pl_regs.IF_ID.inst)}")
        self.screen.addstr(2, 0, f"cycles:\t\t{state.cycles}")
        self.screen.addstr(3, 0, f"pc:\t\t{state.pc}")

        # * If there are more instructions left
        if state.run:
            # * Return if user enters step command (move to next instruction), otherwise break and shutdown
            self.screen.addstr(8, 0, "PAUSED / (q)uit, (s)tep forward")
            while True:
                opt = self.screen.getkey()
                if opt == "q":
                    break
                elif opt == "s":
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
