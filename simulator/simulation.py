import tkinter as tk
from abc import ABC, abstractmethod
from .grid import Grid
from .agent import TKAgent
from .tkinter_utils import rect_pos_to_coordinates
from enum import Enum, auto
from planner import AStarPlanner


class Simulation(ABC):
    DT : int = 50

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
    def __init__(self, grid: Grid, grid_size: int = 10):
        win_w, win_h = grid.width * grid_size, grid.height * grid_size

        # utilities attributes
        self.paused_text = "Paused, press SPACEBAR to resume."
        self.running_text = "Running, press SPACEBAR to pause."
        self.state = State.PAUSED
        self.colors = ["red", "green", "blue", "purple", "yellow"]
        self.cur_color = 0

        # window creation
        self.window = tk.Tk()
        self.window.geometry(f'{win_w}x{win_h + 20}')
        self.window.title("MAPF")
        self.window.resizable(False, False)
        self.canvas = tk.Canvas(self.window, bg='white', width=win_w, height=win_h)
        self.status_label = tk.Label(self.window, text=self.paused_text)
        self.window.bind("<Key>", self.keypress_handler)
        self.canvas.pack()
        self.status_label.pack()

        # Agents creation
        self.agents = []
        for position in grid.agents_init_pos:
            self.agents.append(TKAgent(self.canvas, position, self.get_next_color()))
        #ag1 = TKAgent(self.canvas, (37, 1), self.get_next_color())
        #self.agents = [ag1]

        # Draw vertical lines
        for i in range(grid_size, win_w, grid_size):
            self.canvas.create_line((i, 0, i, win_h), fill="grey")

        # Draw horizontal lines
        for i in range(grid_size, win_h, grid_size):
            self.canvas.create_line((0, i, win_w, i), fill="grey")

        # Draw shelves
        for i in range(grid.height):
            for j in range(grid.width):
                if grid[i][j] == 0:
                    self.canvas.create_rectangle(
                        rect_pos_to_coordinates(j, i),
                        fill="black",
                        outline="black"
                    )
        self.positions = [AStarPlanner.plan(ag.position, (1, 1+i), grid) for i, ag in enumerate(self.agents)]
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
            case _:  # ignore any other keystroke
                pass

    def update(self):
        if self.state == State.RUNNING:
            for i, pos in enumerate(self.positions):
                if len(pos) > 0:
                    new_pos = pos.pop()
                    self.agents[i].move_to(new_pos)


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
