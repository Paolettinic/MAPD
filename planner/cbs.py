from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, List, Dict, Set
from itertools import combinations
from simulator import Grid
from .a_star_planner import AStarPlanner
from .timing import timeit


class ConflictType(Enum):
    VERTEX = auto()
    EDGE = auto()


@dataclass
class Conflict:
    type: ConflictType
    timestep: int
    agent1: int
    agent2: int
    position1: tuple
    position2: tuple | None = None

    def agents(self):
        return self.agent1, self.agent2

    def __str__(self):
        return (
            "CONFLICT:("
            f"{self.type=} "
            f"{self.agent1=} "
            f"{self.agent2=} "
            f"{self.position1=} "
            f"{self.position2=} "
            f"{self.timestep=} "
            ")"
        )


class CBS:

    @classmethod
    @timeit
    def high_level_search(
        cls,
        agents_tasks: Dict[int, Tuple[Tuple, Tuple]],
        grid: Grid,
        timestep: int = 0,
        spatio_temporal_obstacles: Set[Tuple[Tuple, int]] = None
    ) -> Dict[int, List[Tuple]]:
        open_set = set()
        closed_set = set()

        root = CTNode()
        root.constraints = {
            agent_key:
                spatio_temporal_obstacles
                if spatio_temporal_obstacles
                else set()
            for agent_key in agents_tasks
        }
        root.solution = {
            agent_key: AStarPlanner.plan(
                start_position=start_position,
                target_position=target_position,
                grid=grid,
                constraints=root.constraints[agent_key],
                timestep=timestep
            ) for agent_key, (start_position, target_position) in agents_tasks.items()
        }
        root.compute_solution_cost()
        open_set |= {root}
        while open_set:
            p: CTNode = min(open_set, key=lambda node: node.cost)
            open_set -= {p}
            # pprint(open_set)
            closed_set |= {p}
            conflict = cls.get_first_conflict(p.solution)
            # print(conflict)
            if not conflict:
                return p.solution
            constraints = dict()
            if conflict.type == ConflictType.EDGE:
                constraints[conflict.agent1] = {(conflict.position1, conflict.position2, conflict.timestep)}
                constraints[conflict.agent2] = {(conflict.position2, conflict.position1, conflict.timestep)}
            else:
                constraints[conflict.agent1] = {(conflict.position1, conflict.timestep)}
                constraints[conflict.agent2] = {(conflict.position1, conflict.timestep)}
            for agent in [conflict.agent1, conflict.agent2]:
                node_a = deepcopy(p)
                node_a.constraints[agent] |= constraints[agent]
                # print(f"{agent} : {node_a.constraints[agent]}")
                start_position, target_position = agents_tasks[agent]
                node_a.solution[agent] = AStarPlanner.plan(
                    start_position=start_position,
                    target_position=target_position,
                    grid=grid,
                    constraints=node_a.constraints[agent],
                    timestep=timestep
                )
                # print(node_a.solution[agent])
                # print(p.solution[agent])
                # print(node_a.solution[agent] == p.solution[agent])
                if node_a.solution:
                    node_a.compute_solution_cost()
                    if node_a not in closed_set:
                        open_set |= {node_a}
                    # else:
                    # print(f"NODEA for agent {agent} in closed_set")
        print("CBS: NO SOLUTION FOUND")
        return {}

    @staticmethod
    def get_first_conflict(solution: Dict[int, List]) -> Conflict | None:
        # max_len = max(len(solution[a]) for a in solution)
        # padded_sol = {
        #    key: [value[0]] * (max_len - len(value)) + value.copy()
        #    for key, value in solution.items()
        # }
        for (agent1, path1), (agent2, path2) in combinations(solution.items(), 2):
            min_len = min(len(path1), len(path2))
            for i in range(min_len - 1, -1, -1):
                if path1[i] == path2[i]:
                    position, timestep = path1[i]
                    return Conflict(
                        type=ConflictType.VERTEX,
                        agent1=agent1,
                        agent2=agent2,
                        position1=position,
                        timestep=timestep
                    )
            for i in range(min_len - 1, 0, -1):
                (pos11, timestep), (pos12, _), (pos21, _), (pos22, _) = path1[i], path1[i - 1], path2[i], path2[i - 1]
                edge1 = (pos11, pos12)
                edge2 = (pos21, pos22)
                edge2inv = (pos22, pos21)
                if edge1 == edge2 or edge1 == edge2inv:
                    return Conflict(
                        type=ConflictType.EDGE,
                        agent1=agent1,
                        agent2=agent2,
                        position1=pos11,
                        position2=pos12,
                        timestep=timestep
                    )
        return None  # No conflicts found

        # for i in range(max_len - 1, -1, -1):
        #    pos_to_agents = {padded_sol[a][i][0]: [] for a in padded_sol}
        #    for a in padded_sol:
        #        cur_agent_position, t = padded_sol[a][i]
        #        pos_to_agents[cur_agent_position].append(a)
        #        if len(pos_to_agents[cur_agent_position]) > 1:
        #            ag1, ag2 = pos_to_agents[cur_agent_position][:2]
        #            return Conflict(
        #                type=ConflictType.VERTEX,
        #                agent1=ag1,
        #                agent2=ag2,
        #                position1=cur_agent_position,
        #                timestep=t
        #            )
        #    for a in padded_sol:
        #        if i > 0:
        #            cur_agent_position, t1 = padded_sol[a][i]
        #            next_pos, t2 = padded_sol[a][i - 1]
        #            if next_pos in pos_to_agents:
        #                if len(pos_to_agents[next_pos]) > 0:
        #                    conflict_agent = pos_to_agents[next_pos][0]
        #                    if conflict_agent != a:
        #                        return Conflict(
        #                            type=ConflictType.EDGE,
        #                            agent1=a,
        #                            agent2=conflict_agent,
        #                            position1=cur_agent_position,
        #                            position2=next_pos,
        #                            timestep=t1
        #                        )
        # return None

    @classmethod
    def compute_solutions_and_cost(
        cls,
        agents_tasks: Dict[int, Tuple[Tuple, Tuple]],
        grid: Grid,
        constraints: Dict[int, Set[Tuple]],
        spatio_temporal_obstacles: List[Tuple[Tuple, int]],
        timestep: int = 0
    ) -> Tuple[Dict[int, List[Tuple]], int]:
        pass

    @staticmethod
    def solution_cost(solution: Dict[int, List[Tuple]]):
        return sum([len(solution[agent]) for agent in solution])


@dataclass
class CTNode:
    constraints: Dict[int, Set[Tuple[Tuple, int]]] = None
    solution: Dict[int, List[Tuple]] = None
    cost: int = 0

    def __eq__(self, other):
        return (
                isinstance(other, CTNode) and
                self.constraints == other.constraints and
                self.solution == other.solution
        )

    def __hash__(self):
        return hash(
            str(self.constraints) +
            str(self.solution)
        )

    def compute_solution_cost(self):
        self.cost = sum([len(self.solution[agent]) for agent in self.solution])
