from typing import List, Tuple, Union

class Task:
    def __init__(self, s: Tuple | List, g: Tuple | List):
        self.s: Tuple = tuple(s)
        self.g: Tuple = tuple(g)
    def __hash__(self):
        return hash(str(self.s) + str(self.g))

    def __str__(self):
        return f"task(s:{self.s},g:{self.g})"

    def __repr__(self):
        return str(self)

