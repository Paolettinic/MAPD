from typing import Tuple, List, Dict
from dataclasses import dataclass, field
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner
from itertools import combinations
from copy import deepcopy

class CBS:

    @classmethod
    def high_level_search(
        cls,
        agents_tasks: Dict[Agent, Tuple],
        grid: Grid
    ) -> Dict[Agent, List[Tuple]]:
        open_set = set()
        root = ICNode()
        root.solution, root.cost = cls.compute_solutions_and_cost(
            agents_tasks,
            grid,
            root.constraints_dic
        )
        root.cost = cls.solution_cost(root.solution)
        open_set |= {root}
        while open_set:
            p: ICNode = min(open_set, key=lambda n: n.cost)
            conflict = cls.get_conflicts(p.solution)
            if not conflict:
                return p.solution
            *agents, st_position = conflict
            # TODO: MA-CBS goes HERE
            for agent in agents:
                node_a = ICNode()
                node_a.constraints_set = p.constraints_dic
                node_a.constraints_set[agent].append(st_position)
                old_solution_cost = len(p.solution)
                node_a.solution = deepcopy(p.solution)
                node_a.solution[agent] = AStarPlanner.plan(
                    start_position=agent.position,
                    target_position=agents_tasks[agent],
                    grid=grid,
                    constraints=node_a.constraints_set[agent]
                )
                if node_a.solution[agent]:
                    node_a.cost -= old_solution_cost
                    node_a.cost += len(node_a.solution[agent])
                    open_set |= {node_a}

    @staticmethod
    def get_conflicts(solution: Dict[Agent, List]) -> Tuple:
        max_len = max(len(solution[a]) for a in solution)
        padded_sol = {
            key: value.copy() + [value[-1] * (max_len - len(value))]
            for key, value in solution.items()
        }
        for i in range(max_len):
            agents_in_pos = {padded_sol[a][i]: [] for a in padded_sol}
            for a in padded_sol:
                pos = padded_sol[a][i]
                agents_in_pos[pos].append(a)
                if agents_in_pos[pos].len > 1:
                    for ag1, ag2 in combinations(agents_in_pos[pos], 2):
                        return ag1, ag2, pos
        return tuple()

    @classmethod
    def compute_solutions_and_cost(
        cls,
        agent_tasks: Dict[Agent, Tuple],
        grid: Grid,
        constraints: Dict[Agent, List[Tuple]]
    ) -> Tuple[Dict[Agent, List[Tuple]], int]:
        solution = {
            agent: AStarPlanner.plan(
                start_position=agent.position,
                target_position=target_position,
                grid=grid,
                constraints=constraints[agent]
            )
            for agent, target_position in agent_tasks
        }
        cost = cls.solution_cost(solution)
        return solution, cost

    @staticmethod
    def solution_cost(solution: Dict[Agent, List[Tuple]]):
        return sum([len(solution[agent]) for agent in solution])


@dataclass
class ICNode:
    constraints_dic: Dict[Agent, List[Tuple]] = field(default_factory=lambda: dict())
    solution: Dict[Agent, List[Tuple]] = field(default_factory=lambda: dict())
    cost: int = 0

    def __hash__(self):
        return hash(self.solution)
