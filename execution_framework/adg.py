from typing import Dict, List
from planstep import PlanStep


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
