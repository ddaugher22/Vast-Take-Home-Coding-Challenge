# Helium-3 Lunar Mining Simulation

## Overview
Develop a simulation for a lunar Helium-3 space mining operation. This simulation will manage and track the efficiency of mining trucks and unload stations over a continuous 72-hour operation.

## Getting Started
1. Clone the repository: ```git clone [repository_url]```
2. Navigate to the project directory: ```cd Vast-Take-Home-Coding-Challenge```
3. Verify python3 is installed - can check by running ```python3 --version```

## Usage
You can run the simulation from the command line using the following command:
```python3 simulation.py -n <number_of_trucks> -m <number_of_stations>```

## Command-Line Arguments
-n: Number of mining trucks (required).
-m: Number of unload stations (required).

## Output
At the end of the simulation, you will see performance metrics for each truck and station such as:
- Total unloads performed by each truck
- Total unloads received by each station
- Average mining time per truck
- Total time trucks waited at a specific station

## Run Tests
Verify pytest is installed - ```pytest --version```.
If not, run ```pip install pytest```.
  
Make sure to run pytest commands from top level folder.

To run all test cases in the tests folder: ```pytest```
To run all test cases in the tests folder with verbose output: ```pytest -v```
To run a specific test file: ```pytest tests/<file_name>```
To run a specific test function: ```pytest -k <function_name>```

## Design

The simulation is built off of three main classes: MiningTruck, UnloadStation, and TaskQueue
An instance of the TaskQueue, as well as instances for MiningTrucks and UnloadStations are instantiated at the start of the simulation.

A task is an action that can be performed by a mining truck:
1. start mining
2. travel to unload station
3. unload
4. travel to mining station

A mining truck continuously performs tasks in the order shown above, starting again from the top after completing #4.
Each of the above tasks is represented by a function within the MiningTruck class.

The Task Queue is a queue of tuples containing:
1. a task
2. the time the task should be performed

The Task Queue is initialized with a startMining task for each of the trucks in the simulation.

A loop continuously pulls the next task that should be performed from the Task Queue and then runs the task (function of MiningTruck class). The simulation is able to run faster than real-time since it is always skipping to the next timestamp when an event will occur.
When a task is run, it then returns a tuple representing the next task (task, time) that should be performed by that truck.
This tuple is inserted into the Task Queue based on the time the task will be performed.

The loop breaks when the 72 hour mark has been passed, at which point statistics for truck/station performance and efficiency are displayed.

## Things I would implement with more time/in a real world scenario
1. Add a lot more test cases to the unit/integration tests
2. Write a startup script for installing packages (such as verifying pip is installed in order to install pytest)
3. Use a virtual environment
4. Add more statistics (or potentially an efficiency/performance score for each truck/station) to the statistics section after the simulation ends
5. Implement a logging system (add --logging argument) to better visualize the steps taken by each truck if need be
6. Add arguments to the program to change the ordering of the trucks/stations in the post simulation statistics
7. Make simulation run time configurable incase a time other than 72 hours needs to be tested and make default 72 hours (also don't love hardcoding values)
