import pathlib
import tkinter as tk
from abc import ABC, abstractmethod
from .grid import Grid
from .agent import TKAgent
from .tkinter_utils import rect_pos_to_coordinates
from enum import Enum, auto
from planner import AStarPlanner
import json


class Simulation(ABC):
    DT: int = 100

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


class State(Enum):
    RUNNING = auto()
    PAUSED = auto()


class TkinterSimulation(Simulation):
    """

    """
    def __init__(self, grid: Grid, scenario_path: pathlib.Path, grid_size: int = 10):
        self.win_w, self.win_h = grid.width * grid_size, grid.height * grid_size
        self.grid_size = grid_size
        self.grid = grid

        # utilities attributes
        self.paused_text = "Paused, press SPACEBAR to resume."
        self.running_text = "Running, press SPACEBAR to pause."
        self.state = State.PAUSED
        self.colors = ["red", "green", "blue", "purple", "yellow"]
        self.cur_color = 0

        # window creation
        self.window = tk.Tk()
        self.window.geometry(f'{self.win_w + 100}x{self.win_h + 20 + 20}')
        self.window.title("MAPF")
        self.window.resizable(False, False)
        self.canvas = tk.Canvas(self.window, bg='white', width=self.win_w, height=self.win_h)
        self.status_label = tk.Label(self.window, text=self.paused_text)
        self.pos_label = tk.Label(self.window, text="")
        self.window.bind("<Key>", self.keypress_handler)
        self.canvas.bind('<Motion>', self.hover)
        self.canvas.pack()
        self.status_label.pack()
        self.pos_label.pack()
        self.agents = []
        with open(scenario_path, "r") as scenario:
            self.scenario = json.load(scenario)

        self.initialize()

    def initialize(self):

        # Draw vertical lines
        for i in range(self.grid_size, self.win_w, self.grid_size):
            self.canvas.create_line((i, 0, i, self.win_h), fill="grey")

        # Draw horizontal lines
        for i in range(self.grid_size, self.win_h, self.grid_size):
            self.canvas.create_line((0, i, self.win_w, i), fill="grey")

        # Draw shelves
        for pos in self.grid.shelves_pos:
            self.canvas.create_rectangle(
                rect_pos_to_coordinates(*pos),
                fill="#AAA",
                outline="black"
            )

        # Stations creation
        for station in self.scenario["stations_positions"]:
            self.canvas.create_oval(
                rect_pos_to_coordinates(*station),
                fill="pink",
                outline="pink"
            )

        # Agents creation
        for position in self.scenario["agents_positions"]:
            self.agents.append(TKAgent(self.canvas, position, self.get_next_color()))

        # Task assignment
        # TODO: substitute with actual task assignment
        for i, ag in enumerate(self.agents):
            ag.command_queue = [
                {"move_to": pos}
                for pos in AStarPlanner.plan(ag.position, (1, i+1), self.grid)
            ]

    def hover(self, event):
        x, y = event.x, event.y
        self.pos_label.config(text=f"({y//self.grid_size},{x//self.grid_size})")

    def keypress_handler(self, event):
        match event.char:
            case " ":  # Run/Pause simulation toggle
                if self.state == State.RUNNING:
                    self.state = State.PAUSED
                    self.status_label.config(text=self.paused_text)
                elif self.state == State.PAUSED:
                    self.state = State.RUNNING
                    self.status_label.config(text=self.running_text)
                else:
                    raise RuntimeError("Unknown state")
            case "q":  # Press q to quit
                self.window.quit()

            case "k":  # decrease simulation speed
                if self.DT < 500:
                    self.DT += 10

            case "j":  # increase simulation speed
                if self.DT > 20:
                    self.DT -= 10
            case "r":  # reset the simulation
                self.canvas.delete("all")
                self.agents = []
                self.initialize()
            case _:  # ignore any other keystroke
                # print(event.char)
                pass

    def update(self):
        if self.state == State.RUNNING:
            for ag in self.agents:
                ag.execute_command()

                # new_pos = self.positions.pop()
                # self.agents[0].move_to(new_pos)
                # self.status_label.config(text=str(self.agents[0].position))
        self.window.after(self.DT, self.update)

    def get_next_color(self):
        c = self.colors[self.cur_color]
        self.cur_color = (self.cur_color + 1) % len(self.colors)
        return c

    def start(self) -> None:
        self.window.after(self.DT, self.update)
        self.window.mainloop()
