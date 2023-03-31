from utils import *


class Model():
    def __init__(self, observer_function: typing.Callable):
        """ Initialize a new model

            observer_function: function - a function to call when model is updated
        """

        self.state = State()
        self.observer_function = observer_function
