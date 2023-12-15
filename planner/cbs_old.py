from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, List, Dict, Set

from simulator import Grid
from .a_star_planner import AStarPlanner


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
        return f"{self.type=} {self.agent1=} {self.agent2=} {self.position1=} {self.position2=} {self.timestep=}"

class CBS:

    @classmethod
    def high_level_search(
        cls,
        agents_tasks: Dict[int, Tuple[Tuple, Tuple]],
        grid: Grid,
        timestep: int = 0,
        spatio_temporal_obstacles: List[Tuple[Tuple, int]] = None
    ) -> Dict[int, List[Tuple]]:
        st_obs = [] if spatio_temporal_obstacles is None else spatio_temporal_obstacles
        open_set = set()
        closed_set = set()
        node_counter = 0
        root = ICNode(node_counter=node_counter)
        node_counter += 1
        root.constraints_dic = {ak: set() for ak in agents_tasks}
        root.solution, root.cost = cls.compute_solutions_and_cost(
            agents_tasks=agents_tasks,
            grid=grid,
            constraints=root.constraints_dic,
            spatio_temporal_obstacles=st_obs,
            timestep=timestep,
        )
        if not root.solution:
            return {}
        open_set |= {root}
        it = 0
        while open_set:
            #if it > 10:
            #    print("REACHED 10 iterations ")
            #    return {}
            #else:
            #    it += 1
            p: ICNode = min(open_set, key=lambda n: n.cost)
            open_set -= {p}
            closed_set |= {p}
            conflict = cls.get_conflicts(p.solution)
            if not conflict:
                return p.solution
            # TODO: MA-CBS goes HERE
            print(f"{conflict=}")
            constraint = {}
            if conflict.type == ConflictType.EDGE:
                constraint[conflict.agent1] = {(conflict.position1, conflict.timestep),(conflict.position2, conflict.timestep + 1)}
                constraint[conflict.agent2] = {(conflict.position2, conflict.timestep),(conflict.position1, conflict.timestep + 1)}
                print(f"{constraint=}")
            else:
                constraint[conflict.agent1] = {(conflict.position1, conflict.timestep)}
                constraint[conflict.agent2] = {(conflict.position1, conflict.timestep)}
                print(f"{constraint=}")
            print(f"{open_set=}")
            for agent in conflict.agents():
                node_a = deepcopy(p)
                node_a.node_counter = node_counter
                node_counter += 1
                node_a.constraints_dic[agent] |= constraint[agent]
                old_solution_cost = len(p.solution[agent])

                start_position, target_position = agents_tasks[agent]
                node_a.solution[agent] = AStarPlanner.plan(
                    start_position=start_position,
                    target_position=target_position,
                    grid=grid,
                    constraints=list(node_a.constraints_dic[agent]),
                    timestep=timestep
                )
                if node_a.solution[agent]:
                    node_a.cost -= old_solution_cost
                    node_a.cost += len(node_a.solution[agent])
                    if node_a not in closed_set:
                        print(node_a)
                        open_set |= {node_a}
                    else:
                        print("node_a in closed set")
                        print(node_a)

    @staticmethod
    def get_conflicts(solution: Dict[int, List]) -> Conflict | None:
        max_len = max(len(solution[a]) for a in solution)
        padded_sol = {
            key: [value[0]] * (max_len - len(value)) + value.copy()
            for key, value in solution.items()
        }
        for i in range(max_len - 1, -1, -1):
            pos_to_agents = {padded_sol[a][i][0]: [] for a in padded_sol}
            for a in padded_sol:
                cur_agent_position, t = padded_sol[a][i]
                pos_to_agents[cur_agent_position].append(a)
                if len(pos_to_agents[cur_agent_position]) > 1:
                    ag1, ag2 = pos_to_agents[cur_agent_position][:2]
                    return Conflict(
                        type=ConflictType.VERTEX,
                        agent1=ag1,
                        agent2=ag2,
                        position1=cur_agent_position,
                        timestep=t
                    )
                if i > 0:
                    next_pos, t = padded_sol[a][i - 1]
                    if next_pos in pos_to_agents:
                        if len(pos_to_agents[next_pos]) > 0:
                            conflict_agent = pos_to_agents[next_pos][0]
                            if conflict_agent != a:
                                return Conflict(
                                    type=ConflictType.EDGE,
                                    agent1=a,
                                    agent2=conflict_agent,
                                    position1=cur_agent_position,
                                    position2=next_pos,
                                    timestep=t - 1
                                )

        return None

    @classmethod
    def compute_solutions_and_cost(
        cls,
        agents_tasks: Dict[int, Tuple[Tuple, Tuple]],
        grid: Grid,
        constraints: Dict[int, Set[Tuple]],
        spatio_temporal_obstacles: List[Tuple[Tuple, int]],
        timestep: int = 0
    ) -> Tuple[Dict[int, List[Tuple]], int]:
        solution = {
            agent: AStarPlanner.plan(
                start_position=start_position,
                target_position=target_position,
                grid=grid,
                constraints=list(constraints[agent]) + spatio_temporal_obstacles,
                timestep=timestep
            )
            for agent, (start_position, target_position) in agents_tasks.items()
        }
        cost = cls.solution_cost(solution)
        return solution, cost

    @staticmethod
    def solution_cost(solution: Dict[int, List[Tuple]]):
        return sum([len(solution[agent]) for agent in solution])


@dataclass
class ICNode:
    node_counter: int = 0
    constraints_dic: Dict[int, Set[Tuple]] = field(default_factory=lambda: dict())
    solution: Dict[int, List[Tuple]] = field(default_factory=lambda: dict())
    cost: int = 0

    def __eq__(self, other):
        return (
            isinstance(other, ICNode) and
            self.constraints_dic == other.constraints_dic and
            self.solution == other.solution and
            self.cost == other.cost
        )

    def __hash__(self):
        return hash(self.node_counter)
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ICNode:[node_counter:{self.node_counter},const_dict:{self.constraints_dic}]"
