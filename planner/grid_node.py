from typing import List, Set
from simulator.grid import Grid


class GridNode:
    """
    Node class representing positions in the map for tree search
    """

    def __init__(self, position: tuple, timestep: int = 0):
        self.x, self.y = position
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None
        self.timestep = timestep

    def same_position(self, other):
        if isinstance(other, GridNode):
            return self.x == other.x and self.y == other.y
    def __repr__(self):
        return str(self)
    def __str__(self):
        return f"x:{self.x},y:{self.y},t:{self.timestep}"
    def __eq__(self, other):
        if isinstance(other, GridNode):
            return \
                    self.x == other.x and \
                    self.y == other.y and \
                    self.timestep == other.timestep
        return False

    def __hash__(self):
        return hash(f"{self.x},{self.y},{self.timestep}")

    def __lt__(self, other):
        return self.f < other.f

    def manhattan(self, other: "GridNode"):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_valid_positions(self, grid: Grid) -> Set["GridNode"]:
        valid_positions = set()
        adjacent_cells = [
            (self.x, self.y),      # STAY
            (self.x - 1, self.y),  # LEFT
            (self.x + 1, self.y),  # RIGHT
            (self.x, self.y + 1),  # UP
            (self.x, self.y - 1),  # DOWN
        ]
        for pos_x, pos_y in adjacent_cells:
            # checking only if > 0, otherwise the last element is returned
            if pos_x > 0 and pos_y > 0 and grid[pos_y][pos_x] != 0:
                node = GridNode((pos_x, pos_y), self.timestep + 1)
                node.g = self.g + 1

                node.parent = self
                valid_positions.add(node)
        return valid_positions


if __name__ == "__main__":
    print(GridNode((1, 2)).manhattan(GridNode((3, 4))))
