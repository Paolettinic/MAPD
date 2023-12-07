from dataclasses import dataclass


@dataclass
class Task:
    s: tuple
    g: tuple

    def __hash__(self):
        return hash(str(self.s) + str(self.g))

    def __str__(self):
        return f"task(s:{self.s},g:{self.g})"

    def __repr__(self):
        return str(self)


