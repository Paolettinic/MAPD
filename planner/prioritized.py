from typing import List, Tuple, Dict
from .task import Task
from .task_agent_graph import TaskAgentGraph, TaskAgentVertex, TaskAgentEdge
from itertools import product
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner, manhattan_distance
from .algorithm import Algorithm
import elkai
from .timing import timeit


class PrioritizedAgent:
    def __init__(self, agent):
        self.agent = agent

    def update(self):
        self.agent.update()

    def assign_path(self, path: List[Tuple]):
        self.agent.command_queue = [{"move_to": pos} for pos, _ in path]


class PrioritizedTaskPlanning(Algorithm):

    def __init__(self, agents: List[Agent], grid: Grid, tasks: List[Task]):
        self.agents = {i: PrioritizedAgent(agent) for i, agent in enumerate(agents)}
        self.grid = grid
        self.tasks = tasks
        self.graph = self.build_graph()
        self.timestep = 0
        task_assignment, agent_order = self.assign_tasks_to_agents()
        constraint_set = set()
        for agent_key in agent_order:
            path_for_cur_agent = []
            cur_agent_position = self.agents[agent_key].agent.position
            task_list = task_assignment[agent_key]
            timestep = 0
            for task in task_list:
                pos_to_pickup = AStarPlanner.plan(
                    start_position=cur_agent_position,
                    target_position=task.s,
                    grid=self.grid,
                    constraints=constraint_set,
                    timestep=timestep
                )
                timestep += len(pos_to_pickup)
                pickup_to_delivery = AStarPlanner.plan(
                    start_position=task.s,
                    target_position=task.g,
                    grid=self.grid,
                    constraints=constraint_set,
                    timestep=timestep
                )
                cur_agent_position = task.g
                timestep += len(pickup_to_delivery)
                path_for_cur_agent = pickup_to_delivery + pos_to_pickup + path_for_cur_agent

            path_to_start = AStarPlanner.plan(
                start_position=cur_agent_position,
                target_position=self.agents[agent_key].agent.starting_position,
                grid=self.grid,
                constraints=constraint_set,
                timestep=timestep
            )
            path_for_cur_agent = path_to_start + path_for_cur_agent
            self.agents[agent_key].assign_path(path_for_cur_agent)

            for position, ts in path_for_cur_agent:
                constraint_set.add((position, ts))
                constraint_set.add((position, ts+1))

    def add_tasks(self, tasks: List[Task]):
        self.tasks += tasks

    @timeit
    def assign_tasks_to_agents(self) -> Tuple[Dict, List]:
        print("Searching an assignment for tasks")
        # print(f"{self.graph.vertices}")
        distance_matrix = self.graph.get_distance_matrix()
        dm = elkai.DistanceMatrix(distance_matrix)
        hamiltonian_cycle = dm.solve_tsp()
        # print(hamiltonian_cycle)
        current_agent = -1
        task_assignment = {}
        agent_order = []
        for node in hamiltonian_cycle:
            if node < len(self.agents):
                if node in task_assignment:
                    break
                current_agent = node
                agent_order.append(current_agent)
                task_assignment[self.graph.vertices[current_agent].data] = []
            else:
                task_assignment[self.graph.vertices[current_agent].data].append(self.graph.vertices[node].data)
        return task_assignment, agent_order

    def compute_weight(self, vertex1: TaskAgentVertex, vertex2: TaskAgentVertex):
        vertex1_agent = isinstance(vertex1.data, int)
        vertex2_agent = isinstance(vertex2.data, int)
        if not vertex2_agent:
            if vertex1_agent:
                return max(
                    manhattan_distance(self.agents[vertex1.data].agent.starting_position, vertex2.data.s),
                    vertex2.data.r
                )
            return (
                    manhattan_distance(vertex1.data.s, vertex1.data.g) +
                    manhattan_distance(vertex1.data.g, vertex2.data.s)
            )
        if not vertex1_agent:
            return manhattan_distance(vertex1.data.s, vertex1.data.g)
        return 0

    def build_graph(self) -> TaskAgentGraph:
        graph = TaskAgentGraph()
        nodes = 0
        for agent in self.agents:
            graph.add_vertex(TaskAgentVertex(nodes, agent))
            nodes += 1
        for task in self.tasks:
            graph.add_vertex(TaskAgentVertex(nodes, task))
            nodes += 1
        for vertex1, vertex2 in product(graph.vertices, repeat=2):
            graph.add_edge(TaskAgentEdge(vertex1, vertex2, self.compute_weight(vertex1, vertex2)))
        return graph

    def update(self):
        for agent_key in self.agents:
            self.agents[agent_key].update()
        self.timestep += 1
