# MAPD

Multi Agent Pickup and Delivery in warehouse environment, project for the Planning and Reasoning exam.

---
NOTE: this repository uses LKH-3, compiled from soure for linux. The original source files and windows executable is available
[here](http://webhotel4.ruc.dk/~keld/research/LKH-3/)
## Instructions
- Create a conda environment:
```shell
conda create -n mapf -y
```
- Clone this repository
```shell
git clone https://github.com/Paolettinic/MAPD
```
- Move into the main directory
```shell
cd MAPD
```
- Activate the conda env:
```shell
conda activate mapf
```
- Install all the dependencies :
```shell
pip install -r requirements.txt
```
- execute the main file:
```shell
python3 main.py -a "token_passing" --scenario "scenarios/scen1.json"
```
This will execute the algorithm "Token Passing" using the specified scenario; the available algorithms are:
- Token Passing: "token_passing"
- Token Passing with Taks Swaps:  "token_passing_task_swap"
- Central:  "central" (not working on the provided maps, read the report for more information)
- Task Assignment with Prioritized Path Planning:  "prioritized_task_assignment"

