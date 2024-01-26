from typing import Set, List, Tuple, Dict
from .task import Task
from .task_agent_graph import TaskAgentGraph, TaskAgentVertex, TaskAgentEdge
from itertools import product
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner, manhattan_distance
from .algorithm import Algorithm
import elkai
from .timing import timeit


class PrioritizedAgent:
    def __init__(self, agent: Agent):
        self.agent = agent

    def update(self):
        self.agent.update()

    def assign_path(self, path: List[Tuple]):
        self.agent.command_queue = [{"move_to": pos} for pos, _ in path]

    @property
    def position(self):
        return self.agent.position
    
    @property
    def parking_position(self):
        return self.agent.starting_position


class PrioritizedTaskPlanning(Algorithm):

    def __init__(self, agents: List[Agent], grid: Grid, tasks: List[Task]):
        self.agents = {i: PrioritizedAgent(agent) for i, agent in enumerate(agents)}
        self.grid = grid
        self.tasks = tasks
        self.graph = self.build_graph()
        self.timestep = 0
        task_assignment = self.assign_tasks_to_agents()
        constraint_set = set()
        cur_agents_paths = {
            agent_key: self.find_path_for_agent(
                    self.agents[agent_key], 
                    self.timestep,
                    task_assignment[agent_key],
                    set()
                ) 
                for agent_key in task_assignment
        }
        # TODO: Modify the line below to take into account path lengths
        open_agent_set = set(cur_agents_paths.keys())
        while open_agent_set:
            cur_agent = max(open_agent_set, key=lambda ag : len(cur_agents_paths[ag]))
            constraint_set |= set(pos for pos in cur_agents_paths[cur_agent])
            constraint_set |= set((pos, t + 1) for pos, t in cur_agents_paths[cur_agent])
            open_agent_set.remove(cur_agent)
            for agent_key in open_agent_set:
                cur_agents_paths[agent_key] = self.find_path_for_agent(
                    self.agents[agent_key],
                    self.timestep,
                    task_assignment[agent_key],
                    constraint_set
                ) 
        for agent_key in cur_agents_paths:
            self.agents[agent_key].assign_path(cur_agents_paths[agent_key])
            

    def find_path_for_agent(
        self,
        agent: PrioritizedAgent,
        cur_timestep: int,
        task_list: List[Task],
        constraint_set: Set[Tuple[Tuple,int]],
        current_position: Tuple = ()
    ) -> List[Tuple]: 
        timestep = cur_timestep
        cur_agent_position = current_position if current_position else agent.parking_position
        path_for_cur_agent = []
        for task in task_list:
            task_path = self.find_path_for_task(task,cur_agent_position,timestep,constraint_set)
            cur_agent_position = task.g
            timestep += len(task_path)
            path_for_cur_agent = task_path + path_for_cur_agent

        path_to_park = self.find_path_for_parking_location(agent.parking_position, cur_agent_position, timestep, constraint_set)
        path_for_cur_agent = path_to_park + path_for_cur_agent
        return path_for_cur_agent
        
    def find_path_for_task(
        self,
        task: Task,
        cur_agent_position: Tuple,
        timestep: int,
        constraint_set: Set[Tuple[Tuple, int]],
    ) -> List[Tuple]:
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
        return pickup_to_delivery + pos_to_pickup 

    def find_path_for_parking_location(
            self,
            parking_position: Tuple,
            cur_agent_position: Tuple,
            timestep: int,
            constraint_set: Set[Tuple[Tuple, int]],
            ) -> List[Tuple]:
        
        return AStarPlanner.plan(
            start_position=cur_agent_position,
            target_position=parking_position,
            grid=self.grid,
            constraints=constraint_set,
            timestep=timestep
        )

    def add_tasks(self, tasks: List[Task]):
        self.tasks += tasks

    @timeit
    def assign_tasks_to_agents(self) -> Dict[int, List[Task]]:
        print("Searching an assignment for tasks")
        # print(f"{self.graph.vertices}")
        distance_matrix = self.graph.get_distance_matrix()
        distance_matrix = distance_matrix.tolist()
        dm = elkai.DistanceMatrix(distance_matrix)
        hamiltonian_cycle = dm.solve_tsp()
        current_agent = -1
        task_assignment = {}
        for node in hamiltonian_cycle:
            if node < len(self.agents):
                if node in task_assignment:
                    break
                current_agent = node
                task_assignment[self.graph.vertices[current_agent].data] = []
            else:
                task_assignment[self.graph.vertices[current_agent].data].append(self.graph.vertices[node].data)
        return task_assignment 

    def compute_weight(self, vertex1: TaskAgentVertex, vertex2: TaskAgentVertex):
        vertex1_is_agent = isinstance(vertex1.data, int)
        vertex2_is_agent = isinstance(vertex2.data, int)
        if not vertex2_is_agent:
            if vertex1_is_agent:  # vertex2 is a task, vertex1 is an agent
                assert isinstance(vertex2.data, Task)
                assert isinstance(vertex1.data, int)
                return max(
                    manhattan_distance(self.agents[vertex1.data].agent.starting_position, vertex2.data.s),
                    vertex2.data.r
                )
            assert isinstance(vertex1.data, Task)
            assert isinstance(vertex2.data, Task)
            return (  # vertex2 is a task, vertex1 is a task
                    manhattan_distance(vertex1.data.s, vertex1.data.g) +
                    manhattan_distance(vertex1.data.g, vertex2.data.s)
            )
        if not vertex1_is_agent:  # vertex2 is an agent, vertex1 is a task
            assert isinstance(vertex1.data, Task)
            return manhattan_distance(vertex1.data.s, vertex1.data.g)
        # vertex1 is an agent, vertex2 is an agent
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

