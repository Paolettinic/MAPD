import tkinter
from typing import Tuple
from .tkinter_utils import rect_pos_to_coordinates
class Shelf:
    def __init__(self,canvas: tkinter.Canvas, position: Tuple, access_position: Tuple):
        self.position = position
        self.access_position = access_position
        canvas.create_rectangle(
            rect_pos_to_coordinates(*position),
            fill="#AAA",
            outline="black"
        )
        #canvas.create_rectangle(
        #    rect_pos_to_coordinates(*access_position),
        #    fill="#EEE",
        #    outline="gray"
        #)