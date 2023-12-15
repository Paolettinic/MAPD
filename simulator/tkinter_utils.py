from typing import Tuple


def rect_pos_to_coordinates(pos_x, pos_y, cs=10) -> Tuple[int, int, int, int]:
    return pos_x * cs, pos_y * cs, pos_x * cs + cs, pos_y * cs + cs


def move_from_to(start_position: tuple, target_position: tuple, cs=10) -> Tuple:
    return tuple((tp - sp) * cs for tp, sp in zip(target_position, start_position))
