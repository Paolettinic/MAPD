import argparse

import pathlib
from simulator import TkinterSimulation


def main(args):
    simulation = TkinterSimulation(args["scenario"], args["algorithm"])
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
        "-a", "--algorithm",
        help="Name of the algorithm to use"
    )
    parser.add_argument(
        "--scenario",
        type=pathlib.Path,
        help="Path of the scenario file"
    )
    main(vars(parser.parse_args()))
