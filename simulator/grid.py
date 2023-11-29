import pathlib
import numpy as np


class Grid:
    """

    """
    def __init__(self, grid_file: str) -> None:
        """
        :param grid_file:
        """
        with open(grid_file, 'r') as grid:
            next(grid)
            self.height = int(next(grid).split(" ")[1])
            self.width = int(next(grid).split(" ")[1])
            self.grid = np.ones((self.height, self.width))
            self.shelves_pos = []
            self.walls_pos = []
            next(grid)
            for i, row in enumerate(grid):
                for j, cell in enumerate(row):
                    if cell == "T":
                        self.walls_pos.append((j,i))
                        self.grid[i][j] = 0
                    elif cell == "N":
                        self.grid[i][j] = 0
                        self.shelves_pos.append(((j,i),(j,i-1)))
                    elif cell == "S":
                        self.grid[i][j] = 0
                        self.shelves_pos.append(((j,i),(j,i+1)))
                    else:
                        pass

    def save(self, path: pathlib.Path = "saved.map") -> None:
        np.save(path, self.grid)

    def load(self, path: pathlib.Path) -> None:
        self.grid = np.load(path)

    def __str__(self):
        return str(self.grid)

    def __getitem__(self, item):
        return self.grid[item]
