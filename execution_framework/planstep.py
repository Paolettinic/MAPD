from dataclasses import dataclass
@dataclass
class PlanStep:
    t: int
    a: str
    s: tuple
    g: tuple

    def __repr__(self):
        return f"PS:({self.t},{self.a},{self.s},{self.g})"

    def __hash__(self):
        return hash(f"{self.t}{self.a}{self.s}{self.g}")