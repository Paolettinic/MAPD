from .algorithm import Algorithm
from .central import Central
from .token_passing import TokenPassing
from .token_passing_task_swap import TokenPassingTaskSwap
from .prioritized import PrioritizedTaskPlanning
def get_algorithm(algorithm_name: str, *args, **kwargs) -> Algorithm:
    match algorithm_name:
        case "central":
            return Central(*args, **kwargs)
        case "token_passing":
            return TokenPassing(*args, **kwargs)
        case "token_passing_task_swap":
            return TokenPassingTaskSwap(*args, **kwargs)
        case "prioritized_task_assignment":
            return PrioritizedTaskPlanning(*args, **kwargs)
        case _:
            raise NotImplementedError(f"The desired algorithm [{algorithm_name}] was not implemented")

