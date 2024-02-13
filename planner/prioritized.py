from enum import Enum, auto 
from typing import Set, List, Tuple, Dict
from .task import Task
from .task_agent_graph import TaskAgentGraph, TaskAgentVertex, TaskAgentEdge
from itertools import product
from simulator import Agent, Grid
from .a_star_planner import AStarPlanner, manhattan_distance
from .algorithm import Algorithm
from .timing import timeit
import os

class AgentStatus(Enum):
    pickup = auto()
    delivery = auto()


class PrioritizedAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.has_finished_all_tasks = False
        self.assigned_tasks : List[Task] = []
        self.current_task_index = 0
        self.status = AgentStatus.pickup

    def update(self):
        self.agent.update()
        if self.current_task_index < len(self.assigned_tasks):
            if self.status == AgentStatus.pickup:
                if self.position == self.assigned_tasks[self.current_task_index].s:
                    self.status = AgentStatus.delivery
            elif self.status == AgentStatus.delivery:
                if self.position == self.assigned_tasks[self.current_task_index].g:
                    self.status = AgentStatus.pickup
                    self.current_task_index += 1 
                    if self.current_task_index >= len(self.assigned_tasks):
                        return
                    new_task = self.assigned_tasks[self.current_task_index]
                    self.agent.assign_pickup_delivery(new_task.s, new_task.g)
        else:
            self.has_finished_all_tasks = True 

    def assign_path(self, path: List[Tuple]):
        self.agent.command_queue = [{"move_to": pos} for pos, _ in path]

    @property
    def position(self):
        return self.agent.position
    
    @property
    def parking_position(self):
        return self.agent.starting_position


class PrioritizedTaskPlanning(Algorithm):
    LKH_PATH = "planner/LKH-3.0.9"
    PROBLEM_FILE_NAME = "problem.tsp"
    PARAMETER_FILE_NAME = "parameters.par"
    TOUR_FILE_NAME = "solution.tour"
    OUTPUT_TOUR_FILE_NAME = "out_solution.tour"
    PROBLEM_FILE = os.path.join(LKH_PATH, PROBLEM_FILE_NAME) 
    PARAMETER_FILE = os.path.join(LKH_PATH, PARAMETER_FILE_NAME)
    TOUR_FILE = os.path.join(LKH_PATH, TOUR_FILE_NAME)
    OUTPUT_TOUR_FILE = os.path.join(LKH_PATH, OUTPUT_TOUR_FILE_NAME)
    LKH_EXECUTABLE = os.path.join(LKH_PATH, "LKH")

    PARAMETER_VALUES = {
        "PROBLEM_FILE": f"{PROBLEM_FILE}",
        "TIME_LIMIT": "100",
        "TRACE_LEVEL": "1",
        "TOUR_FILE": f"{TOUR_FILE}",
        "OUTPUT_TOUR_FILE": f"{OUTPUT_TOUR_FILE}",
        "RUNS" : "10",
        "SEED": "123",
        "MOVE_TYPE": "5",
        "PATCHING_C": "3",
        "MAKESPAN" : "YES",
        "POPULATION_SIZE" : "10"
    }
    PROBLEM_VALUES = {
        "NAME": "TA-Prioritized",
        "COMMENT": "TA-prioritized",
        "TYPE": "ATSP",
        "DIMENSION": "", # this has to be changed with len(agents) + len(tasks)
        "EDGE_WEIGHT_TYPE": "EXPLICIT",
        "EDGE_WEIGHT_FORMAT": "FULL_MATRIX",
    }

    def __init__(self, agents: List[Agent], grid: Grid, tasks: List[Task]):
        self.agents = {i: PrioritizedAgent(agent) for i, agent in enumerate(agents)}
        self.grid = grid
        self.tasks = tasks
        self.graph = self.build_graph()
        self.timestep = 0
        self.makespan = -1
        task_assignment = self.assign_tasks_to_agents()
        for ag_k in task_assignment:
            if task_assignment[ag_k]:
                self.agents[ag_k].assigned_tasks = task_assignment[ag_k]
                first_task = task_assignment[ag_k][0]
                self.agents[ag_k].agent.assign_pickup_delivery(first_task.s, first_task.g)
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

    def lkh_solve(self, distance_matrix) -> List[int]:
        import time
        # writing parameter file
        with open(self.PARAMETER_FILE, 'w+') as parameter_file:
            #parameter_file.write("SPECIAL\n")
            for key, value in self.PARAMETER_VALUES.items():
                parameter_file.write(key + " = " + value + "\n")
        # writing problem file
        with open(self.PROBLEM_FILE, 'w+') as problem_file:
            self.PROBLEM_VALUES["DIMENSION"] = str(len(distance_matrix))
            for key, value in self.PROBLEM_VALUES.items():
                problem_file.write(key + " : " + value + "\n")
            problem_file.write("EDGE_WEIGHT_SECTION\n")
            for row in distance_matrix:
                problem_file.write(" ".join(str(int(val)) for val in row) + "\n")
            #problem_file.write("TIME_WINDOW_SECTION\n")
            #for i in range(len(self.agents)):
            #    problem_file.write(f"{i+1} {-1} {10000}\n")
            #for i, task in enumerate(self.tasks):
            #    problem_file.write(f"{i + len(self.agents) + 1} {task.r} {10000}\n")

            problem_file.write("EOF\n")

        print("solving using LKH")
        os.system(self.LKH_EXECUTABLE + " " + self.PARAMETER_FILE)
        print("LKH solver returned, waiting 2 seconds for file to write...")
        time.sleep(2)
        print("Opening generated tour file...")
        with open(self.TOUR_FILE, 'r') as solution_file:
            while not "TOUR_SECTION" in solution_file.readline():
                pass
            tour = [int(s) - 1 for s in solution_file.readlines()[:-2]]
            tour += [tour[0]]
        return tour

    @timeit
    def assign_tasks_to_agents(self) -> Dict[int, List[Task]]:
        print("Searching an assignment for tasks")
        # print(f"{self.graph.vertices}")
        distance_matrix = self.graph.get_distance_matrix()
        #with open("matrix.np",'w') as dmfile:
        #    for row in distance_matrix:
        #        dmfile.write(" ".join(str(el) for el in row))
        #        dmfile.write("\n")

        distance_matrix = distance_matrix.tolist()

        hamiltonian_cycle = self.lkh_solve(distance_matrix)
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
        print({agent: len(task_assignment[agent]) for agent in task_assignment})
        return task_assignment 

    def compute_weight(self, vertex1: TaskAgentVertex, vertex2: TaskAgentVertex):
        vertex1_is_agent = isinstance(vertex1.data, int)
        vertex2_is_agent = isinstance(vertex2.data, int)
        if not vertex2_is_agent:
            if vertex1_is_agent:  # vertex1 is an agent, vertex2 is a task
                assert isinstance(vertex1.data, int)
                assert isinstance(vertex2.data, Task)
                return max(
                    manhattan_distance(self.agents[vertex1.data].parking_position, vertex2.data.s),
                    vertex2.data.r
                )
            assert isinstance(vertex1.data, Task)
            assert isinstance(vertex2.data, Task)
            return (  # vertex1 is a task, vertex2 is a task
                    manhattan_distance(vertex1.data.s, vertex1.data.g) +
                    manhattan_distance(vertex1.data.g, vertex2.data.s) 
            )
        if not vertex1_is_agent:  # vertex1 is a task , vertex2 is an agent
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
        if self.makespan == -1:
            if all([agent.has_finished_all_tasks for agent in self.agents.values()]):
                self.makespan = self.timestep
        for agent_key in self.agents:
            self.agents[agent_key].update()
        self.timestep += 1

