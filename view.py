from utils import *


class View:
    def __init__(self):
        """Initialize a new view"""

        pass

    def rerender(self, state: State):
        """Rerender the view"""

        print(f"cycle_count:\t{state.stats.cycles}")
        print(f"pc:\t\t{state.pc}")
