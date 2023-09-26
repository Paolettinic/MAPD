from typing import List
from grid import Grid


class GridNode:
    """
    Node class representing positions in the map for tree search
    """
    def __init__(self, position: tuple):
        self.x, self.y = position
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __eq__(self, other):
        if isinstance(other, GridNode):
            return self.x == other.x and self.y == other.y
        return False

    def __lt__(self, other):
        return self.f < other.f

    def manhattan(self, other: "GridNode"):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_valid_positions(self, grid: Grid) -> List:
        valid_positions = []
        adjacent_cells = [
            (self.x - 1, self.y),  # LEFT
            (self.x + 1, self.y),  # RIGHT
            (self.x, self.y + 1),  # UP
            (self.x, self.y - 1),  # DOWN
        ]
        for pos_x, pos_y in adjacent_cells:
            if pos_x > 0 and pos_y > 0 and grid[pos_y][pos_x] == 1:
                valid_positions.append((pos_x, pos_y))

        return valid_positions
