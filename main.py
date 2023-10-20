#!/
import argparse

import pathlib
from simulator import Grid
from simulator import TkinterSimulation


def main(args):
    warehouse_grid = Grid(args["map"])
    simulation = TkinterSimulation(warehouse_grid, args["scenario"])
    simulation.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simulates the chosen MAPF algorithm in a warehouse environment',
    )
    parser.add_argument(
        "-s", "--simulator",
        default="Tkinter",
        help="Which simulator to use; currently supported: Tkinter (default), CoppeliaSim"
    )

    parser.add_argument(
        "map",
        type=pathlib.Path,
        help="Path of the map file"
    )

    parser.add_argument(
        "scenario",
        type=pathlib.Path,
        help="Path of the scenario file"
    )
    main(vars(parser.parse_args()))
