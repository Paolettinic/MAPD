from dataclasses import dataclass
from typing import List, Tuple, Hashable, Callable
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner, manhattan_distance


class TPAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.free = True
        self.requires_token = True
        self.task = None
        self.final = self.agent.position

    def update(self):
        if len(self.agent.command_queue) <= 1:
            self.requires_token = True
        # if self.final == self.agent.position:
        #    self.requires_token = True
        self.agent.update()

    def assign_path(self, path):
        self.agent.command_queue = [{"move_to": pos} for pos in path]
        self.final = path[0]


@dataclass
class Task:
    s: Tuple
    g: Tuple

    def __hash__(self):
        return hash(str(self.s) + str(self.g))

    def __str__(self):
        return f"task(s:{self.s},g:{self.g})"

    def __repr__(self):
        return str(self)


@dataclass
class Token:
    paths: dict
    tasks: List[Task]
    assign: dict


class TokenPassing:
    def __init__(self, agents: List[Agent], grid: Grid):
        self.grid = grid
        self.tp_agents = {ag: TPAgent(agent) for ag, agent in enumerate(agents)}
        self.token = Token(
            paths={ag: [self.tp_agents[ag].agent.position] for ag in self.tp_agents},
            tasks=[],
            assign={ag: None for ag in self.tp_agents}
        )
        self.timestep = 0

    def create_constraints_for_agent(self, agent: Hashable):
        constraints = list()
        for ag in self.token.paths:
            if agent != ag:
                for t, pos in enumerate(reversed(self.token.paths[ag])):
                    if t >= self.timestep:
                        constraints.append((pos, t + self.timestep))  # vertex conflict constraint
                        constraints.append((pos, t + self.timestep + 1))  # edge conflict constraint
        return constraints

    def assign_path_to_agent(self, agent: Hashable, path_function: Callable = None, **kwargs):
        constraints = self.create_constraints_for_agent(agent)
        if "path" in kwargs:
            path = kwargs["path"]
        elif path_function is not None:
            # print("AGENT",agent)
            path = path_function(agent=self.tp_agents[agent], constraints=constraints, **kwargs)
        else:
            raise RuntimeError("Either specify a path or a path_function")
        self.token.paths[agent] = path
        print("PATH FOR AGENT", agent)
        print(list(zip(path,[self.timestep + len(path) - i for i in range(len(path))])))
        print("CONSTRAINTS FOR AGENT", agent)
        print(constraints)
        self.tp_agents[agent].assign_path(path)

    def add_tasks(self, new_tasks: List[Task]):
        # Add all new task, if any to the task set T
        self.token.tasks += new_tasks

    def path1(self, agent: TPAgent, task: Task, constraints: List, **kwargs):
        pos_to_pickup = AStarPlanner.plan(agent.agent.position, task.s, self.grid, constraints, timestep=self.timestep)
        pickup_to_end = AStarPlanner.plan(task.s, task.g, self.grid, constraints,
                                          timestep=self.timestep + len(pos_to_pickup) - 1)
        return pickup_to_end + pos_to_pickup

    def path2(self, agent: TPAgent, constraints: List, **kwargs):
        path = AStarPlanner.plan(agent.agent.position, agent.agent.starting_position, self.grid, constraints,
                                 timestep=self.timestep)
        return path

    def update(self):
        while any([self.tp_agents[ag].requires_token for ag in self.tp_agents]):
            for agent in self.tp_agents:
                if self.tp_agents[agent].requires_token:
                    print(agent)
                    # Token is assigned to agent
                    self.tp_agents[agent].requires_token = False
                    endpoints = [self.token.paths[ag][0] for ag in self.token.paths if ag != agent]
                    clear_tasks = [
                        t for t in self.token.tasks
                        if t.s not in endpoints and t.g not in endpoints
                    ]
                    tasks_with_goal_eq_agent_pos = {
                        t for t in self.token.tasks if t.g == self.tp_agents[agent].agent.position
                    }
                    # tasks_with_goal_eq_agent_pos = {
                    #    ag for ag in self.tp_agents if self.tp_agents[agent].agent.position in endpoints and ag != agent
                    # }
                    if len(clear_tasks) > 0:
                        print(agent, "clear task")
                        task = min(
                            clear_tasks,
                            key=lambda t: manhattan_distance(self.tp_agents[agent].agent.position, t.s)
                        )
                        self.token.assign[agent] = task
                        self.token.tasks.remove(task)
                        self.assign_path_to_agent(agent, path_function=self.path1, task=task)
                    elif len(tasks_with_goal_eq_agent_pos) == 0 and self.tp_agents[
                        agent].agent.position not in endpoints:
                        print(agent, "STAY")
                        print(tasks_with_goal_eq_agent_pos)
                        print(self.tp_agents[agent].agent.position)
                        print(endpoints)
                        self.assign_path_to_agent(agent, path=[self.tp_agents[agent].agent.position])
                    else:
                        print(tasks_with_goal_eq_agent_pos)
                        print(agent, "GOTO START")
                        # path = self.path2(self.tp_agents[agent])
                        # print(path)
                        # print(self.tp_agents[agent].agent)
                        self.assign_path_to_agent(agent, path_function=self.path2)
        for agent in self.tp_agents:
            self.tp_agents[agent].update()
        self.timestep += 1
