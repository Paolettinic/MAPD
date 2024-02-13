from typing import Tuple, Dict, List, Any
from abc import ABC, abstractmethod
import tkinter as tk
from .tkinter_utils import rect_pos_to_coordinates, move_from_to, eqt_pos_to_coordinates


class Agent(ABC):
    """

    """
    starting_position: Tuple
    position: Tuple
    task: object
    command_queue: List

    @abstractmethod
    def move_to(self, position: Tuple) -> None:
        ...

    @abstractmethod
    def pickup(self, shelf_position: Tuple) -> None:
        ...

    @abstractmethod
    def unload(self) -> None:
        ...

    @abstractmethod
    def update(self) -> None:
        ...
    @abstractmethod
    def assign_pickup_delivery(self, pickup: Tuple, delivery: Tuple) -> None:
        ...

class TKAgent(Agent):
    """

    """

    def __init__(self, canvas: tk.Canvas, position: Tuple, color: str = "red") -> None:
        self.starting_position = position
        self.position = position
        self.task = None
        self.canvas = canvas
        self.color = color
        self.pickup_location = self.position
        self.delivery_location = self.position
        self.pickup_handler = self.canvas.create_polygon(
            eqt_pos_to_coordinates(*self.pickup_location),
            fill=color
        )
        self.delivery_handler = self.canvas.create_polygon(
            eqt_pos_to_coordinates(*self.pickup_location),
            fill=color
        )
        self.handler = self.canvas.create_oval(
            rect_pos_to_coordinates(*position),
            fill=color
        )
        self.command_queue: List[Dict[str, Any]] = []

    def update(self) -> None:
        if len(self.command_queue) > 0:
            command = self.command_queue.pop()
            action, arg = next(iter(command.items()))
            match action:
                case "move_to":
                    self.move_to(arg)
                case "pickup":
                    self.pickup(arg)
                case "unload":
                    self.pickup(arg)
                case _:
                    pass

    def move_to(self, position: Tuple) -> None:
        if not isinstance(position, tuple):
            print(position)
        self.canvas.move(
            self.handler,
            *move_from_to(
                self.position,
                position
            )
        )
        self.position = position

    def assign_pickup_delivery(self, pickup: Tuple, delivery: Tuple) -> None:
        self.canvas.move(
            self.pickup_handler,
            *move_from_to(
                self.pickup_location,
                pickup
            )
        )
        self.canvas.move(
            self.delivery_handler,
            *move_from_to(
                self.delivery_location,
                delivery
            )
        )
        self.pickup_location = pickup
        self.delivery_location = delivery

    def pickup(self, shelf_position: Tuple) -> None:
        pass

    def unload(self) -> None:
        pass

    def __str__(self):
        return self.color
