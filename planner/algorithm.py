from abc import ABC, abstractmethod
from typing import List
from .task import Task
from simulator import Agent, Grid


class Algorithm(ABC):
    timestep: int
    makespan: int
    @abstractmethod
    def __init__(self, agents: List[Agent], grid: Grid, tasks: List[Task]):
        ...
    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def add_tasks(self, tasks: List[Task]):
        ...

