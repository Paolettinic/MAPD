import tkinter as tk
from abc import ABC, abstractmethod
from map import Map
from agent import TKAgent
from utils import rect_pos_to_coords, move_from_to
from enum import Enum, auto
class Simulation(ABC):
    DT = 1000

    @abstractmethod
    def start(self) -> None:
        pass

    # @abstractmethod
    # def pause(self) -> None:
    #     pass
    #
    # @abstractmethod
    # def resume(self) -> None:
    #     pass
    #
    # @abstractmethod
    # def make_agent_perform_action(self, agents: List, actions: List) -> None:
    #     pass
    #
    # @abstractmethod
    # def add_order_to_dispatcher(self, order: Any, dispatcher: Any) -> None:
    #     pass

class State(Enum):
    RUNNING = auto()
    PAUSED = auto()

class TkinterSimulation(Simulation):


    def __init__(self, map: Map, grid_size: int = 10):

        self.colors = ["red", "green", "blue", "purple", "yellow"]
        self.cur_color = 0
        self.window = tk.Tk()
        win_w, win_h = map.width * grid_size, map.height * grid_size
        self.window.geometry(f'{win_w}x{win_h}')
        self.window.resizable(False, False)
        self.window.title("Canvas")
        self.canvas = tk.Canvas(self.window, bg='white', width=win_w, height=win_h)
        self.canvas.pack()
        #ag1 = self.canvas.create_rectangle(self._pos_to_coords(1,1), fill=self.get_next_color())
        ag1 = TKAgent(self.canvas, (1,1), self.get_next_color())
        self.agents = [ag1]
        for i in range(grid_size, win_w, grid_size):
            self.canvas.create_line((i, 0, i, win_h), fill="grey")
        for i in range(grid_size, win_h, grid_size):
            self.canvas.create_line((0, i, win_w, i), fill="grey")
        for i in range(map.height):
            for j in range(map.width):
                if map.map[i][j] == 0:
                    self.canvas.create_rectangle(
                        rect_pos_to_coords(j, i),
                        fill="black",
                        outline="black"
                    )
        self.window.bind("<Key>", self.toggle_state)
        self.state = State.PAUSED
        self.positions = [(2,4),(2,3),(2,2),(2,1)]

    def toggle_state(self, event):
        if event.char == " ":
            if self.state == State.RUNNING:
                self.state = State.PAUSED
            elif self.state == State.PAUSED:
                self.state = State.RUNNING
            else:
                raise RuntimeError("Unknown state")
    def update(self):
        #print("update")
        #if self.state == State.PAUSED:
        #    self.window.mainloop()
        print(self.state)
        if self.state == State.RUNNING:
            if len(self.positions) > 0:
                new_pos = self.positions.pop()
                self.agents[0].move_to(new_pos)
        self.window.after(self.DT, self.update)

    def get_next_color(self):
        c = self.colors[self.cur_color]
        self.cur_color = (self.cur_color + 1) % len(self.colors)
        return c


    def start(self) -> None:
        self.window.after(self.DT, self.update)
        self.window.mainloop()
