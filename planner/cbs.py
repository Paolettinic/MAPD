from typing import Tuple, List, Dict
from dataclasses import dataclass, field
from simulator import int, Grid
from .a_star_planner import AStarPlanner
from copy import deepcopy


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
        root = ICNode()
        root.solution, root.cost = cls.compute_solutions_and_cost(
            agents_tasks=agents_tasks,
            grid=grid,
            constraints=root.constraints_dic,
            spatio_temporal_obstacles=st_obs,
            timestep=timestep,
        )
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
                start_position, target_position = agents_tasks[agent]
                node_a.solution[agent] = AStarPlanner.plan(
                    start_position=start_position,
                    target_position=target_position,
                    grid=grid,
                    constraints=node_a.constraints_set[agent],
                    timestep=timestep
                )
                if node_a.solution[agent]:
                    node_a.cost -= old_solution_cost
                    node_a.cost += len(node_a.solution[agent])
                    open_set |= {node_a}

    @staticmethod
    def get_conflicts(solution: Dict[int, List]) -> Tuple:
        max_len = max(len(solution[a]) for a in solution)
        padded_sol = {
            key: value.copy() + [value[-1] * (max_len - len(value))]
            for key, value in solution.items()
        }
        for i in range(max_len):
            pos_to_agents = {padded_sol[a][i][0]: [] for a in padded_sol}
            for a in padded_sol:
                cur_agent_position, t = padded_sol[a][i]
                pos_to_agents[cur_agent_position].append(a)
                if len(pos_to_agents[cur_agent_position]) > 1:
                    ag1, ag2 = pos_to_agents[cur_agent_position][:2]
                    return ag1, ag2, cur_agent_position, t
                if i < max_len:
                    next_pos, t = padded_sol[a][i+1]
                    if next_pos in pos_to_agents:
                        conflict_agent = pos_to_agents[next_pos][0]
                        if conflict_agent != a:
                            return a, conflict_agent, next_pos, t

        return tuple()

    @classmethod
    def compute_solutions_and_cost(
        cls,
        agents_tasks: Dict[int, Tuple[Tuple, Tuple]],
        grid: Grid,
        constraints: Dict[int, List[Tuple]],
        spatio_temporal_obstacles: List[Tuple[Tuple,int]],
        timestep: int = 0
    ) -> Tuple[Dict[int, List[Tuple]], int]:
        solution = {
            agent: AStarPlanner.plan(
                start_position=start_position,
                target_position=target_position,
                grid=grid,
                constraints=constraints[agent] + spatio_temporal_obstacles,
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
    constraints_dic: Dict[int, List[Tuple]] = field(default_factory=lambda: dict())
    solution: Dict[int, List[Tuple]] = field(default_factory=lambda: dict())
    cost: int = 0

    def __hash__(self):
        return hash(self.solution)
