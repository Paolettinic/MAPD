from typing import List
from queue import PriorityQueue
from dataclasses import dataclass, field


@dataclass(order=True)
class Order:
    priority: int
    products: List[int] = field(compare=False)


class OrderSimulator:

    def __init__(self) -> None:
        self.orders = PriorityQueue()

    def add_order_list(self, orders):
        for o in orders:
            self.orders.put(o)

    def add_order(self, order: Order) -> None:
        self.orders.put(order)

    def get_order(self) -> Order:
        return self.orders.get() if not self.orders.empty() else None
