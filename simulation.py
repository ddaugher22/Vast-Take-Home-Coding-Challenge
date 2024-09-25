import argparse
import random
import constants as const


class MiningTruck():
    time = 0
    def __init__(self):
        pass
    def goToMiningLocation(self):
        return((self.startMining, const.TRAVEL_TIME))
    def goToUnloadStation(self):
        return((self.unload, const.TRAVEL_TIME))
    def startMining(self):
        # Mining trucks spend a random amount of time between 1 and 5 hours at mining locations
        # Get a random time between 1 and 5 hours in seconds 
        miningTime = random.randint(3600, 18000)
        self.time += miningTime
        return((self.goToUnloadStation, self.time + miningTime))
    def unload(self):
        pass

class UnloadStation():
    queue = []
    def __init__(self):
        pass

class TaskQueue():
    queue = []
    def __init__(self):
        pass
    def enqueue(self, task):
        time = task[1]
        i = 0
        while i < len(self.queue):
            if time >= self.queue[i][1]:
                i += 1
            else:
                break
        self.queue = self.queue[:i] + [task] + self.queue[i:]

    def getCurrentTask(self):
        nextTask = self.queue[0]
        self.queue = self.queue[1:]
        return nextTask

def RunSimulation():
    # Get number of mining trucks (n) and number of unload stations (m)
    n, m = ParseArgs()

    miningTrucks = []
    unloadStations = []
    taskQueue = TaskQueue()

    for i in range(n):
        miningTrucks.append(MiningTruck())
        # each truck starts at a mining location so the first task added to the queue for each truck will be to mine
        taskQueue.enqueue((miningTrucks[-1].startMining,0))
    
    for i in range(m):
        unloadStations.append(UnloadStation())

    time = 0
    while True:
        task, time = taskQueue.getCurrentTask()
        
        # if the simulation time passes the 72 hour mark, break
        if time > const.TOTAL_SIM_TIME:
            break

        nextTask = task()
        taskQueue.enqueue(nextTask)
            # Display results here

def ParseArgs():
    # Parse command line arguments for number of mining trucks and number of unload stations
    parser = argparse.ArgumentParser(description='Get number of mining trucks and unload station')
    parser.add_argument('-n', '--numTrucks', type=int, help='Number of mining trucks', required=True)
    parser.add_argument('-m', '--unloadStations', type=int, help='Number of unload stations', required=True)
    args = parser.parse_args()
    return args.numTrucks, args.unloadStations


if __name__ == '__main__':
    RunSimulation()
