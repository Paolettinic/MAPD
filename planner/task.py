from typing import List, Tuple, Union

class Task:
    def __init__(self, s: Tuple | List, g: Tuple | List, r: int = 0):
        self.s: Tuple = tuple(s)
        self.g: Tuple = tuple(g)
        self.r: int = r
    def __hash__(self):
        return hash(str(self.s) + str(self.g) + str(self.r))

    def __eq__(self, other):
        if other:
            return isinstance(other, Task) and self.s == other.s and self.g == other.g and self.r == other.r
        return False
    def __str__(self):
        return f"task(s:{self.s},g:{self.g})"

    def __repr__(self):
        return str(self)

