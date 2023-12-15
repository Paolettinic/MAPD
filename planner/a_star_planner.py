from .grid_graph import GridNode, GridEdge
from queue import PriorityQueue
from typing import Tuple, Set
from simulator import Grid


class AStarPlanner:

    # TODO: change lines 25:26. Time to find node in fringe should be O(1).
    @classmethod
    def plan(
        cls,
        start_position: Tuple,
        target_position: Tuple,
        grid: Grid,
        constraints:Set[tuple] = None,
        timestep=0,
        get_time: bool = True
    ):
        #print(f"A* CONSTRAINTS: {constraints}")
        constraints_vertex_set = set()
        constraints_edge_set = set()
        if constraints is not None:
            for constraint in constraints:
                if len(constraint) == 2: # VERTEX
                    constraints_vertex_set.add(GridNode(*constraint))
                elif len(constraint) == 3: # EDGE
                    constraints_edge_set.add(GridEdge(*constraint))
        start = GridNode(start_position, timestep=timestep)
        target = GridNode(target_position)
        start.g = 0
        start.h = start.manhattan(target)
        start.f = start.g + start.h
        fringe = PriorityQueue()
        closed = set()
        fringe.put(start)

        # print(f"ASTAR: {constraints_grid_set=}")
        while not fringe.empty():
            n: GridNode = fringe.get()
            closed.add(n)
            if n.same_position(target):
                return cls._get_path(n, get_time)
            # neighbors = {adj for adj in n.get_valid_positions(grid) if adj not in constraints_grid_set}
            neighbors = n.get_valid_positions(grid, get_time) - constraints_vertex_set
            for adj_node in neighbors:
                edge = GridEdge((n.x, n.y),(adj_node.x, adj_node.y), n.timestep)
                if edge in constraints_edge_set:
                    continue
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
        while node.parent:
            node: GridNode = node.parent
            path.append(node.get_path_step(get_time))
        return path


def manhattan_distance(pos_a: tuple, pos_b: tuple):
    return abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])
