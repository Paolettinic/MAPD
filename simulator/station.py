from typing import Tuple, List, Callable
from .order import Order

class Station:
    def __init__(self, position: Tuple):
        self.position: Tuple = position
        self.order: Order = None

    def assign_order(self, order: Order):
        self.order = order
