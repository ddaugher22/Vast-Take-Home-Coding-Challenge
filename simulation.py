import argparse
import random
import constants as const

class MiningTruck():

    def __init__(self, task_queue):
        # each truck starts at a mining location - add a mining task to the task queue when a truck is instantiated
        task_queue.enqueue((self.startMining, 0))
    
        # Class attrs for tracking mining truck mining/unload statistics
        self.total_unloads = 0
        self.total_times_mined = 0
        self.time_spent_waiting = 0
        self.time_spent_mining = 0
        self.times_traveled = 0

    def goToMiningLocation(self, cur_time):
        self.times_traveled += 1
        return((self.startMining, cur_time + const.TRAVEL_TIME))
    
    def goToUnloadStation(self, cur_time):
        self.times_traveled += 1
        return((self.unload, cur_time + const.TRAVEL_TIME))
    
    def startMining(self, cur_time):
        # Mining trucks spend a random amount of time between 1 and 5 hours at mining locations
        # Get a random time between 1 and 5 hours in seconds 
        mining_time = random.randint(3600, 18000)
        self.time_spent_mining += mining_time
        self.total_times_mined += 1

        return((self.goToUnloadStation, cur_time + mining_time))
    
    def unload(self, cur_time, station):
        self.time_spent_waiting += station.queueTime(cur_time)
        
        station.enqueue(cur_time)
        return (self.goToMiningLocation, cur_time + station.queueTime(cur_time))

class UnloadStation():
    
    def __init__(self):
        self.queue = []
        self.start_time = None
    
        self.time_spent_waiting = 0
        self.total_unloads_completed = 0


    def inUse(self):
        return len(self.queue) > 0
    
    def queueTime(self, cur_time):
        if not self.inUse():
            return 0
        return len(self.queue)*const.UNLOAD_TIME - (cur_time - self.start_time)
    
    def enqueue(self, cur_time):

        self.time_spent_waiting += self.queueTime(cur_time)

        if not self.inUse():
            self.start_time = cur_time
   
        self.queue.append(cur_time)
    
    def startNextUnload(self, cur_time):
        
        self.total_unloads_completed += 1

        self.queue = self.queue[1:]

        if len(self.queue):
            self.start_time = self.queue[0]

        return None
        
        
class TaskQueue():

    def __init__(self):
        self.queue = []
    
    def enqueue(self, task):
        time = task[1]
        i = 0
        while i < len(self.queue):
            if time < self.queue[i][1]:
                break
            i += 1
        self.queue.insert(i, task)

    def getCurrentTask(self):
        nextTask = self.queue[0]
        self.queue = self.queue[1:]
        return nextTask

def getNextUnloadStation(stations, cur_time):
    mn = None
    mnStation = None
    for station in stations:
        if not station.inUse():
            return station
        unload_time = station.queueTime(cur_time)
        if not mn or unload_time < mn:
            mn = unload_time
            mnStation = station
    return mnStation

def RunSimulation(n, m):
   
    # Set up objects - add more description here
    task_queue = TaskQueue()
    mining_trucks = [MiningTruck(task_queue) for i in range(n)]
    unload_stations = [UnloadStation() for i in range(m)]
    
    while True:
        # Pull next item from task queue; each item in the queue is a tuple in the form of (task, time)
        task, time = task_queue.getCurrentTask()
        print(time, task.__name__)
        # Verify the simulation time hasn't passed the 72 hour mark; if it does, break
        if time > const.TOTAL_SIM_TIME:
            break

        if task.__name__ == 'unload':
            station = getNextUnloadStation(unload_stations, time)
            nextTask = task(time, station)
            task_queue.enqueue((station.startNextUnload, time+station.queueTime(time)))
        else:
            nextTask = task(time)

        if nextTask:
            task_queue.enqueue(nextTask)
    
    # Display results here
    for i in mining_trucks:
        print(i.time_spent_mining)
        print(i.total_times_mined)


def ParseArgs():
    # Parse arguments for number of mining trucks (n) and number of unload stations (m)
    parser = argparse.ArgumentParser(description='Get number of mining trucks and unload station')
    parser.add_argument('-n', '--numTrucks', type=int, help='Number of mining trucks', required=True)
    parser.add_argument('-m', '--unloadStations', type=int, help='Number of unload stations', required=True)
    args = parser.parse_args()
    return args.numTrucks, args.unloadStations


if __name__ == '__main__':
    # Get number of mining trucks (n) and number of unload stations (m)
    n, m = ParseArgs()
    
    RunSimulation(n, m)
