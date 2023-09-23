def rect_pos_to_coords(posx, posy, cs=10) -> tuple:
    return posx * cs, posy * cs, posx * cs + cs, posy * cs + cs
def move_from_to(start_position: tuple, target_position: tuple, cs=10):
    """

    :param start_position:
    :param target_position:
    :param cs:
    :return:
    """
    return ((tp - sp) * cs for tp, sp in zip(target_position,start_position))