from .task import Task
from simulator import int
from enum import Enum, auto
from typing import List, Dict, Any, Tuple, Union
from simulator import Grid
from .a_star_planner import manhattan_distance
from .cbs import CBS
import numpy as np
from scipy.optimize import linear_sum_assignment


class Status(Enum):
    BUSY: auto()
    FREE: auto()
    RESTING: auto()

class TargetPosition(Enum):
    PICKUP: auto()
    DELIVERY: auto()
    PARK: auto()

class CAgent:
    def __init__(self, agent: int):
        self.agent = agent
        self.status = Status.FREE
        self.target = TargetPosition.PARK
    @property
    def position(self):
        return self.agent.position

    def update(self):
        if len(self.agent.command_queue) <= 1:
            if self.target == TargetPosition.PICKUP:
                self.status = Status.RESTING
            else:
                self.status = Status.FREE
        else:
            self.status = Status.BUSY
        self.agent.update()

    def assign_path(self, path):
        self.agent.command_queue = [{"move_to": pos} for pos, _ in path]


class Central:
    def __init__(self, agents: List[int], grid: Grid):
        self.c_agents: Dict[int, CAgent] = {ag: CAgent(agent) for ag, agent in enumerate(agents)}
        self.parking_locations = [agent.starting_position for agent in agents]
        self.grid = grid
        self.timestep = 0
        self.tasks: List[Task] = []
        self.executed_tasks = []
        self.task_assignment_dict = {}
        self.location_assignments = {ag: self.c_agents[ag].position for ag in self.c_agents}
        self.current_paths: Dict[int,List[Tuple[Tuple,int]]] = {ag: [] for ag in agents}
    def assign_task_to_agent(self, agent_key, task, target):
        self.task_assignment_dict[task] = agent_key
        self.location_assignments[agent_key] = task.g
        self.executed_tasks.append(task)
        self.c_agents[agent_key].target = target


    def distance_from_agent(self, agent_key):
        return lambda p: manhattan_distance(self.c_agents[agent_key].position, p)

    def build_cost_matrix(self, free_agents: List[int], endpoints: List[Dict[str, Any]]):
        C = max([max(e["costs"]) for e in endpoints]) + 1
        cost_matrix = np.zeros((len(free_agents), len(endpoints)))
        for i, agent_k in enumerate(free_agents):
            for j, endpoint in enumerate(endpoints):
                if endpoint["type"] == TargetPosition.PICKUP:
                    cost_matrix[i][j] = len(free_agents) * C * endpoint["cost"][i]
                else:
                    cost_matrix[i][j] = len(free_agents) * C**2 * endpoint["cost"][i]

        return cost_matrix


    def assign_endpoints(self, free_agents : List[int]):
        tasks = []
        unexecuted_tasks = [t for t in self.tasks if t not in self.executed_tasks]
        for task in unexecuted_tasks:
            tasks_to_check = self.executed_tasks + tasks
            for ex_task in tasks_to_check:
                if task.s == ex_task.g or task.g == ex_task.g:
                    break
            else:
                tasks.append(task)
        endpoints = [
            {
                "type": TargetPosition.PICKUP,
                "position": task.s,
                "costs" : [manhattan_distance(self.c_agents[ak].position, task.s) for ak in free_agents]
            } for task in tasks
        ]
        num_free_agents = len(free_agents)
        if len(endpoints) < num_free_agents:
            parking_locations_copy = self.parking_locations.copy()
            for agent in free_agents:
                p_loc = min(parking_locations_copy, key=self.distance_from_agent(agent))
                parking_locations_copy.remove(p_loc)
                endpoints.append({
                    "type": TargetPosition.PARK,
                    "position": p_loc,
                    "costs": [manhattan_distance(self.c_agents[ak].position, p_loc) for ak in free_agents]
                })
        cost_matrix = self.build_cost_matrix(free_agents, endpoints)
        cols, rows = linear_sum_assignment(cost_matrix)
        return {
            free_agents[i]: {
                "type": endpoints[j]["type"],
                "position": endpoints[j]["position"]
            } for i, j in zip(cols, rows)
        }

    def update(self):
        # consider all the agents that rests in a pickup position of un-executed task
        unexecuted_tasks = [t for t in self.tasks if t not in self.executed_tasks]
        free_agents = [ag for ag in self.c_agents if self.c_agents[ag].status == Status.FREE]
        resting_agents = [ag for ag in self.c_agents if self.c_agents[ag].status == Status.RESTING]
        # endpoints = {agent_k: {"type": TargetPosition.PARK, "position":self.c_agents[agent_k].position} for agent_k in self.c_agents}
        endpoints = {agent_k: dict() for agent_k in self.c_agents}
        for agent_k in resting_agents:
            cur_agent: CAgent = self.c_agents[agent_k]
            for t in unexecuted_tasks:
                if (
                    cur_agent.position == t.s and
                    self.task_assignment_dict[t] is None and
                    not any([self.location_assignments[a] == t.g for a in self.c_agents])
                ):
                    self.assign_task_to_agent(agent_k, t, TargetPosition.DELIVERY)
                    endpoints[agent_k] = {"type": TargetPosition.DELIVERY, "position":t.g}

        endpoints.update(self.assign_endpoints(free_agents))
        self.assign_paths_to_agents(endpoints)
        for agent_key in self.c_agents:
            self.c_agents[agent_key].update()
            match self.c_agents[agent_key].status:
                case Status.FREE:
                    self.current_paths[agent_key] = []
                    self.location_assignments[agent_key] = self.c_agents[agent_key].position
                case Status.RESTING:
                    self.current_paths[agent_key] = []
                    self.location_assignments[agent_key] = self.c_agents[agent_key].position
                case Status.BUSY:
                    pass

        self.timestep += 1


    def assign_paths_to_agents(self, endpoints: Dict[int,Dict[str, Union[TargetPosition, Tuple]]]):
        agents_tasks = {
            ak: (
                self.c_agents[ak].position,
                endpoints[ak]["position"]
            ) for ak in endpoints
            if endpoints[ak] is not None
        }
        spatio_temporal_obstacles = [st_pos for path in self.current_paths.values() for st_pos in path]
        solutions = CBS.high_level_search(agents_tasks, self.grid, self.timestep, spatio_temporal_obstacles)
        for agent_key, path in solutions.items():
            self.assign_path_to_agent(agent_key, path, endpoints)


    def assign_path_to_agent(self, agent_key, path, endpoints):
        self.current_paths[agent_key] = path
        self.location_assignments[agent_key] = endpoints[agent_key]["position"]
        self.c_agents[agent_key].target = endpoints[agent_key]["type"]
        self.c_agents[agent_key].assign_path(path)


    def add_tasks(self, task_list: List[Task]):
        self.tasks += task_list
        self.task_assignment_dict.update({t: None for t in task_list})
