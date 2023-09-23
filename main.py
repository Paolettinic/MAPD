#!/
import argparse

import cv2
import cv2 as cv
import pathlib
from map import Map
from simulation import Simulation, TkinterSimulation


def main(args):
    warehouse_map = Map(args["map"])
    simulation = TkinterSimulation(warehouse_map)

    simulation.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simulates the chosen MAPF algorithm in a warehouse environment',
    )
    parser.add_argument(
        "-s","--simulator",
        default="OpenCV",
        help="Which simulator to use; currently supported: OpenCV (default), CoppeliaSim"
    )
    parser.add_argument(
        "map",
        type=pathlib.Path,
        help="Path of the map file"
    )
    args = parser.parse_args()
    main(vars(args))