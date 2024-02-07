# MAPD

Multi Agent Pickup and Delivery in warehouse environment, project for the Planning and Reasoning exam.

---
NOTE: this repository uses LKH-3, compiled from soure for linux. The original source files and windows executable is available
[here](http://webhotel4.ruc.dk/~keld/research/LKH-3/)
## Instructions
- Create a conda environment:

        conda create mapf
- Clone this repository

        git clone https://github.com/Paolettinic/MAPD
- Move into the main directory

        cd MAPD
- Activate the conda env:

        conda activate mapf
- execute the main file:

        python main.py -a "token_passing" --scenario "scenarios/scen1.json"

This will execute the algorithm "Token Passing" using the specified scenario; the available algorithms are:
- Token Passing: "token_passing"
- Token Passing with Taks Swaps:  "token_passing_task_swap"
- Central:  "central" 
- Task Assignment with Prioritized Path Planning:  "prioritized_task_assignment"

