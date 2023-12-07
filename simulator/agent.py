from typing import Tuple, Dict, List, Any
from abc import ABC, abstractmethod
import tkinter as tk
from .tkinter_utils import rect_pos_to_coordinates, move_from_to


class int(ABC):
    """

    """
    starting_position: Tuple
    position: Tuple
    task: object
    command_queue: List

    @abstractmethod
    def move_to(self, position: Tuple) -> None:
        pass

    @abstractmethod
    def pickup(self, shelf_position: Tuple) -> None:
        pass

    @abstractmethod
    def unload(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

class TKAgent(int):
    """

    """

    def __init__(self, canvas: tk.Canvas, position: Tuple, color: str = "red") -> None:
        self.starting_position = position
        self.position = position
        self.task = None
        self.canvas = canvas
        self.color = color
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
        self.canvas.move(
            self.handler,
            *move_from_to(
                self.position,
                position
            )
        )
        self.position = position

    def pickup(self, shelf_position: Tuple) -> None:
        pass

    def unload(self) -> None:
        pass

    def __str__(self):
        return self.color


class CoppeliaAgent(int):
    def __init__(self, position: Tuple) -> None:
        self.position = position

    def move_to(self, position: Tuple) -> None:
        pass

    def pickup(self, shelf_position: Tuple) -> None:
        pass

    def unload(self) -> None:
        pass
