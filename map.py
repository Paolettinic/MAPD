import pathlib
import numpy as np


class Map:
    """

    """
    def __init__(self, map_file: pathlib.Path) -> None:
        """
        :param map_file:
        """
        with open(map_file, 'r') as map:
            next(map)
            self.height = int(next(map).split(" ")[1])
            self.width = int(next(map).split(" ")[1])
            self.map = np.ones((self.height, self.width))
            next(map)
            for i, row in enumerate(map):
                for j, cell in enumerate(row):
                    if cell == "T":
                        self.map[i][j] = 0

    def save(self, path: pathlib.Path = "saved.map") -> None:
        np.save(path, self.map)

    def load(self, path: pathlib.Path) -> None:
        self.map = np.load(path)

    def __str__(self):
        return str(self.map)


