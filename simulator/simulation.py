import json
import pathlib
import tkinter as tk
from abc import ABC, abstractmethod
from enum import Enum, auto

from numpy import random

from planner.algorithm_utils import get_algorithm
from planner import Algorithm, Task
from .agent import TKAgent
from .grid import Grid
from .shelf import Shelf
from .tkinter_utils import rect_pos_to_coordinates


class Simulation(ABC):
    DT: int = 100

    @abstractmethod
    def start(self) -> None:
        ...


class State(Enum):
    RUNNING = auto()
    PAUSED = auto()


class TkinterSimulation(Simulation):
    """

    """

    def __init__(self, scenario_path: pathlib.Path, algorithm: str, grid_size: int = 10):
        self.algorithm_name = algorithm
        # scenario opening
        with open(scenario_path, "r") as scenario:
            self.scenario = json.load(scenario)
        grid = Grid(self.scenario["map"])
        self.win_w, self.win_h = grid.width * grid_size, grid.height * grid_size
        self.grid_size = grid_size
        self.grid = grid

        # utilities attributes
        self.paused_text = "Paused, press SPACEBAR to resume."
        self.running_text = "Running, press SPACEBAR to pause."
        self.state = State.PAUSED
        self.colors = ["red", "green", "blue", "purple", "yellow", "pink"]
        self.cur_color = 0

        # window creation
        self.window = tk.Tk()
        self.window.geometry(f'{self.win_w + 100}x{self.win_h + 20 + 20 + 20}')
        self.window.title("MAPF")
        self.window.resizable(False, False)
        self.canvas = tk.Canvas(self.window, bg='white', width=self.win_w, height=self.win_h)
        self.status_label = tk.Label(self.window, text=self.paused_text)
        self.pos_label = tk.Label(self.window, text="")
        self.timestep_label = tk.Label(self.window, text="Timestep: 0")
        self.window.bind("<Key>", self.keypress_handler)
        self.canvas.bind('<Motion>', self.hover)
        self.canvas.pack()
        self.status_label.pack()
        self.pos_label.pack()
        self.timestep_label.pack()
        self.agents = []
        self.shelves = []
        self.initial_tasks = self.scenario["tasks"]
        self.tp = None
        self.tasks = None
        self.algorithm = None
        self.initialize()

    def initialize(self):
        # Draw vertical lines
        for i in range(self.grid_size, self.win_w, self.grid_size):
            self.canvas.create_line((i, 0, i, self.win_h), fill="grey")

        # Draw horizontal lines
        for i in range(self.grid_size, self.win_h, self.grid_size):
            self.canvas.create_line((0, i, self.win_w, i), fill="grey")
        # Draw walls
        for wall_pos in self.grid.walls_pos:
            self.canvas.create_rectangle(rect_pos_to_coordinates(*wall_pos), fill="black")
        # Draw shelves
        self.shelves = []
        for pos, acc in self.grid.shelves_pos:
            self.shelves.append(Shelf(self.canvas, pos, acc))

        # Stations creation
        for station in self.scenario["stations_positions"]:
            self.canvas.create_rectangle(
                rect_pos_to_coordinates(*station),
                fill="orange",
                outline="red"
            )
        # Uncomment this code to create a random set of tasks in a txt file, copy the resulting set in 
        # a scenario json file
        #no_tasks = 100
        #with open("tasks.txt","w") as task_file:
        #    for i in range(no_tasks):
        #        picked_shelf : Shelf = random.choice(self.shelves, size=1)[0]
        #        ts = picked_shelf.access_position
        #        tg = self.scenario["stations_positions"][random.choice(range(len(self.scenario["stations_positions"])),1)[0]]
        #        task_file.write("{"+f"'s':[{ts[0]},{ts[1]}], 'g':[{tg[0]},{tg[1]}], 'r':0"+"}")
        #return   

        # Agents creation
        self.agents = []
        for position in self.scenario["agents_positions"]:
            self.agents.append(TKAgent(self.canvas, tuple(position), self.get_next_color()))

        # Task assignment
        # self.tp = TokenPassing(self.agents, self.grid)
        self.tasks = [Task(**task) for task in self.scenario["tasks"]]
        # self.tp.add_tasks(self.tasks)
        self.algorithm: Algorithm = get_algorithm(
            algorithm_name=self.algorithm_name,
            agents=self.agents,
            grid=self.grid,
            tasks=self.tasks
        )
        # self.algorithm.add_tasks(self.tasks)

    def update(self):
        if self.state == State.RUNNING:
            self.algorithm.update()
            self.timestep_label.config(text=f"Timestep: {self.algorithm.timestep}")
        self.window.after(self.DT, self.update)

    def get_next_color(self):
        c = self.colors[self.cur_color]
        self.cur_color = (self.cur_color + 1) % len(self.colors)
        return c

    def start(self) -> None:
        self.window.after(self.DT, self.update)
        self.window.mainloop()

    def hover(self, event):
        x, y = event.x, event.y
        self.pos_label.config(text=f"({x // self.grid_size},{y // self.grid_size})")

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
                self.initialize()

            case _:  # ignore any other keystroke
                pass
