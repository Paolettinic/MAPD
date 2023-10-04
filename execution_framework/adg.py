from typing import Dict, List
from planstep import PlanStep
from pprint import pprint
class ADG:
    @classmethod
    def from_plans(cls, plans: Dict[str, List[PlanStep]]):
        graph = {}
        for agent in plans:  # Build Type1 edges
            current_step = plans[agent][0]
            graph[current_step] = []
            for i in range(1, len(plans[agent])):
                step = plans[agent][i]
                graph[step] = []
                graph[current_step].append(step)
                current_step = step

        for agent_i in plans:  # Build Type2 edges
            for plan_step_i in plans[agent_i]:
                for agent_j in plans:
                    if agent_i != agent_j:
                        for plan_step_j in plans[agent_j]:
                            if plan_step_i.s == plan_step_j.g and plan_step_i.t <= plan_step_j.t:
                                graph[plan_step_i].append(plan_step_j)
                                break
        return graph

if __name__ == "__main__":
    plans = {
        "r1":[
            PlanStep(0, "n", (0, 0), (0, 1)),
            PlanStep(1, "s", (0, 1), (0, 2)),
            PlanStep(2, "w", (0, 3), (0, 4)),
            PlanStep(3, "e", (0, 4), (0, 5))
        ],
        "r2": [
            PlanStep(0, "n", (1, 0), (1, 1)),
            PlanStep(1, "e", (1, 1), (1, 2)),
            PlanStep(2, "w", (1, 2), (0, 2)),
            PlanStep(3, "s", (0, 2), (0, 3))
        ]
    }
    pprint(ADG.from_plans(plans))