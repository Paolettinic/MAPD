from .grid_node import GridNode
from queue import PriorityQueue


class AStarPlanner:

    # TODO: change lines 25:26. Time to find node in fringe should be O(1).
    @classmethod
    def plan(cls, start_position, target_position, grid, constraints: list[tuple] = None, timestep = 0, get_time: bool = True):
        # print(f"CONSTRAINTS: {constraints}")
        if constraints is not None:
            constraints_grid_set = {GridNode(*constraint) for constraint in constraints}
        else:
            constraints_grid_set = set()
        # print(constraints_grid_set)
        start = GridNode(start_position, timestep=timestep)
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
            if n.same_position(target):
                return cls._get_path(n, get_time)
            #neighbors = {adj for adj in n.get_valid_positions(grid) if adj not in constraints_grid_set}
            neighbors = n.get_valid_positions(grid, get_time) - constraints_grid_set
            for adj_node in neighbors:
                cur_t = adj_node.timestep
                if adj_node in closed:
                    continue
                if adj_node in fringe.queue:  # already visited
                    new_cost = adj_node.g
                    for node in fringe.queue:  # retrieve g,h info
                        if adj_node == node:
                            adj_node = node
                            adj_node.timestep = cur_t
                            break
                    if new_cost < adj_node.g:
                        adj_node.parent = n
                        adj_node.g = new_cost
                        adj_node.f = adj_node.g + adj_node.h

                else:
                    adj_node.h = adj_node.manhattan(target)
                    adj_node.f = adj_node.g + adj_node.h
                    adj_node.parent = n
                    fringe.put(adj_node)
        return cls._get_path(start)

    @classmethod
    def _get_path(cls, node: GridNode, get_time: bool = True):
        path = [node.get_path_step(get_time)]
        while node.parent.parent:
            node: GridNode = node.parent
            path.append(node.get_path_step(get_time))
        return path


def manhattan_distance(pos_a: tuple, pos_b: tuple):
    return abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])