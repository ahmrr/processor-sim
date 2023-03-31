from utils import *


class View:
    def __init__(self):
        """Initialize a new view"""
        pass

    def rerender(self, state: State):
        """ """
        print(f"cycle_count:\t{state.stats['cycle_count']}")
        print(f"pc:\t\t{state.pc}")
        pass
