from utils import *
import curses


class View:
    def __init__(self, step_mode: bool):
        """Initialize a new view"""

        print(f"step:\t\t{step_mode}")

        self.step = step_mode

        self.screen = curses.initscr()
        self.screen.keypad(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        if curses.has_colors():
            curses.start_color()

        if self.step:
            self.rerender = self.rerender_step
        else:
            self.renderer = self.rerender_nostep

    def rerender_nostep(self, state: State):
        """Rerender the view without prompting for user input"""

        self.screen.clear()

        self.screen.addstr(0, 0, f"binary inst:\t{state.pl_regs.IF_ID.inst:#032b}")
        self.screen.addstr(1, 0, f"MIPS inst:\t{decode_inst(state.pl_regs.IF_ID.inst)}")
        self.screen.addstr(2, 0, f"cycles:\t\t{state.cycles}")
        self.screen.addstr(3, 0, f"pc:\t\t{state.pc}")

        if not state.run:
            while self.screen.getkey() != "q":
                pass

            curses.echo()
            curses.nocbreak()
            curses.curs_set(True)
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()

            sys.exit(0)

    def rerender_step(self, state: State):
        """Rerender the view with prompt for user input (continue)"""

        self.screen.clear()

        self.screen.addstr(0, 0, f"binary inst:\t{state.pl_regs.IF_ID.inst:#032b}")
        self.screen.addstr(1, 0, f"MIPS inst:\t{decode_inst(state.pl_regs.IF_ID.inst)}")
        self.screen.addstr(2, 0, f"cycles:\t\t{state.cycles}")
        self.screen.addstr(3, 0, f"pc:\t\t{state.pc}")

        if state.run:
            self.screen.addstr(8, 0, "(q)uit, (s)tep")

            while True:
                opt = self.screen.getkey()
                if opt == "q":
                    break
                elif opt == "s":
                    return

        else:
            self.screen.addstr(8, 0, "(q)uit")

            while self.screen.getkey() != "q":
                pass

        curses.echo()
        curses.nocbreak()
        curses.curs_set(True)
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()

        sys.exit(0)
