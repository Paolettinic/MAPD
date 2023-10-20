from .grid_node import GridNode
from queue import PriorityQueue


class AStarPlanner:

    # TODO: change lines 25:26. Time to find node in fringe should be O(1).
    @classmethod
    def plan(cls, start_position, target_position, grid):
        start = GridNode(start_position)
        target = GridNode(target_position)
        start.g = 0
        start.h = start.manhattan(target)
        start.f = start.g + start.h
        fringe = PriorityQueue()
        closed = set()
        fringe.put(start)

        while not fringe.empty():
            n: GridNode = fringe.get()
            closed.add(n)
            if n == target:
                return cls._get_path(n)
            new_cost = n.g + 1
            neighbors = n.get_valid_positions(grid)
            for adj_pos in neighbors:
                adj_node = GridNode(adj_pos)

                if adj_node in closed:
                    continue

                if adj_node in fringe.queue:  # already visited
                    for node in fringe.queue:  # retrieve g,h info
                        if node == adj_node:
                            adj_node = node
                            break
                    if new_cost < adj_node.g:
                        adj_node.parent = n
                        adj_node.g = new_cost
                        adj_node.f = adj_node.g + adj_node.h

                else:
                    adj_node.g = new_cost
                    adj_node.h = adj_node.manhattan(target)
                    adj_node.f = adj_node.g + adj_node.h
                    adj_node.parent = n
                    fringe.put(adj_node)
        raise RuntimeWarning(f"Target position {target_position} unreachable")

    @classmethod
    def _get_path(cls, node: GridNode):
        path = []
        while node.parent:
            path.append((node.x, node.y))
            node = node.parent
        return path
