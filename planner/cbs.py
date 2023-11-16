from typing import Tuple, Set, List
from dataclasses import dataclass, field
from simulator import Agent

class CBS:
    def __init__(self):
        pass


@dataclass
class Constraint:
    agent: Agent
    vertex: Tuple
    timestep: int

@dataclass
class ICNode:
    constraints_set: Set
    solution: List[List[Tuple]]
    total_cost: int