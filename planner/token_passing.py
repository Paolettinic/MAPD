from dataclasses import dataclass
from typing import List, Set, Callable, Tuple
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner, manhattan_distance
from .task import Task
from .algorithm import Algorithm


class TPAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.requires_token = True
        self.task = None
        self.final = self.agent.position

    def update(self):
        if len(self.agent.command_queue) <= 1:
            self.requires_token = True
        self.agent.update()

    def assign_path(self, path):
        self.agent.command_queue = [{"move_to": pos} for pos, _ in path]
        self.final, _ = path[0]


@dataclass
class Token:
    paths: dict
    tasks: List[Task]
    assign: dict


class TokenPassing(Algorithm):
    def __init__(self, agents: List[Agent], grid: Grid, tasks: List[Task]):
        self.grid = grid
        self.tp_agents = {ag: TPAgent(agent) for ag, agent in enumerate(agents)}
        self.timestep = 0
        self.token = Token(
            paths={
                ag: [(self.tp_agents[ag].agent.position, self.timestep)]
                for ag in self.tp_agents
            },
            tasks=tasks,
            assign={ag: None for ag in self.tp_agents}
        )

    def create_constraints_for_agent(self, agent: int) -> Set[Tuple]:
        constraints = set()
        for ag in self.token.paths:
            if agent != ag:
                for pos, t in self.token.paths[ag]:
                    constraints.add((pos, t))  # vertex conflict constraint
                    constraints.add((pos, t + 1))  # edge conflict constraint
        return constraints

    def assign_path_to_agent(self, agent: int, path_function: Callable = None, **kwargs):
        constraints = self.create_constraints_for_agent(agent)
        if "path" in kwargs:
            path = kwargs["path"]
        elif path_function is not None:
            path = path_function(agent=self.tp_agents[agent], constraints=constraints, **kwargs)
        else:
            raise RuntimeError("Either specify a path or a path_function")
        self.token.paths[agent] = path
        self.tp_agents[agent].assign_path(path)

    def add_tasks(self, new_tasks: List[Task]):
        self.token.tasks += new_tasks

    def path1(self, agent: TPAgent, task: Task, constraints: Set[Tuple], **kwargs):
        pos_to_pickup = AStarPlanner.plan(
            start_position=agent.agent.position,
            target_position=task.s,
            grid=self.grid,
            constraints=constraints,
            timestep=self.timestep
        )
        pickup_to_end = AStarPlanner.plan(
            start_position=task.s,
            target_position=task.g,
            grid=self.grid,
            constraints=constraints,
            timestep=self.timestep + len(pos_to_pickup)
        )
        return pickup_to_end + pos_to_pickup

    def path2(self, agent: TPAgent, constraints: Set[Tuple], **kwargs):
        return AStarPlanner.plan(
            start_position=agent.agent.position,
            target_position=agent.agent.starting_position,
            grid=self.grid,
            constraints=constraints,
            timestep=self.timestep
        )

    def update(self):
        while any([self.tp_agents[ag].requires_token for ag in self.tp_agents]):
            for agent in self.tp_agents:
                cur_agent = self.tp_agents[agent]
                if cur_agent.requires_token:
                    # Token is assigned to agent
                    cur_agent.requires_token = False

                    endpoints = [
                        self.token.paths[ag][0][0]
                        for ag in self.token.paths
                        if ag != agent
                    ]

                    clear_tasks = [
                        t for t in self.token.tasks
                        if t.s not in endpoints and t.g not in endpoints
                    ]

                    tasks_with_goal_eq_agent_pos = {
                        t for t in self.token.tasks
                        if t.g == cur_agent.agent.position
                    }

                    if len(clear_tasks) > 0:
                        task = min(
                            clear_tasks,
                            key=lambda t: manhattan_distance(cur_agent.agent.position, t.s)
                        )
                        self.token.assign[agent] = task
                        self.token.tasks.remove(task)
                        self.assign_path_to_agent(agent, path_function=self.path1, task=task)

                    elif len(tasks_with_goal_eq_agent_pos) == 0 and cur_agent.agent.position not in endpoints:
                        self.assign_path_to_agent(agent, path=[(cur_agent.agent.position, self.timestep)])

                    else:
                        self.assign_path_to_agent(agent, path_function=self.path2)

        for agent in self.tp_agents:
            self.tp_agents[agent].update()
        self.timestep += 1
