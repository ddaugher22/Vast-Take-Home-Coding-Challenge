import argparse
import random
import datetime
import constants as const

class MiningTruck():
    ''' Represents a mining truck that continuously performs the following work flow:
            goToMiningLocation
            startMining
            goToUnloadStation
            unload

        Attributes:
            total_unloads (int): Number of times this truck unloaded it's mined Helium-3 at an unload station
            total_times_mined (int): Number of times this truck mined Helium-3 at a mining location
            time_spent_waiting (int): Total time in seconds this truck spent waiting at an unload station (in the event all stations were in use when the truck arrived)
            time_spent_mining (int): Total time in seconds this truck spent mining at mining locations
            times_traveled (int): Total number of times this truck traveled between mining locations and the unload station
    '''

    def __init__(self, id, task_queue):
        ''' Initialize a MiningTruck '''
        
        self.id = id

        # Each truck starts the simulation at a mining location - add a mining task to the 'task queue' upon the instantiation of a MiningTruck
        task_queue.enqueue((self.startMining, 0))
    
        # Variables for tracking a MiningTruck instance's statistics throughout the simulation
        self.total_unloads = 0
        self.total_times_mined = 0
        self.time_spent_waiting = 0
        self.time_spent_mining = 0
        self.times_traveled = 0

    def goToMiningLocation(self, cur_time):
        ''' Travel to a mining location from the unload station.

            Args:
                cur_time (int): Time at which the truck begins traveling to the mining location
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        '''
        
        self.times_traveled += 1

        return((self.startMining, cur_time + const.TRAVEL_TIME))
    
    def goToUnloadStation(self, cur_time):
        ''' Travel to an unload station from the mining location after a mining operation has been completed.

            Args:
                cur_time (int): Time at which the truck begins traveling to the unload station
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        '''

        self.times_traveled += 1
        
        return((self.unload, cur_time + const.TRAVEL_TIME))
    
    def startMining(self, cur_time):
        ''' Start the mining process for this truck. Mining time is a random time in seconds between 1 and 5 hours.

            Args:
                cur_time (int): Time at which the truck begins the mining operation
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        '''

        # Get a random time between 1 and 5 hours in seconds, representing the amount of time this truck will spend mining
        mining_time = random.randint(3600, 18000)
        
        self.time_spent_mining += mining_time
        self.total_times_mined += 1

        return((self.goToUnloadStation, cur_time + mining_time))
    
    def unload(self, cur_time, station):
        ''' Start the unloading process of Helium-3 at the specified unload station.

            Args:
                cur_time (int): Time at which the truck begins traveling to the mining location
                station (instance): Instance of the station this truck is currently unloading or waiting to unload at
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        '''
        queue_time = station.queueTime(cur_time)
        self.time_spent_waiting += queue_time
       
        station.enqueue(self, cur_time+queue_time)
        return (self.goToMiningLocation, cur_time + queue_time)


class UnloadStation():
    ''' Represents an unload station where mining trucks unload Helium-3.

        Attributes:
            total_unloads (int): Number of times this truck unloaded it's mined Helium-3 at an unload station
            total_times_mined (int): Number of times this truck mined Helium-3 at a mining location
            time_spent_waiting (int): Total time in seconds this truck spent waiting at an unload station (in the event all stations were in use when the truck arrived)
            time_spent_mining (int): Total time in seconds this truck spent mining at mining locations
            times_traveled (int): Total number of times this truck traveled between mining locations and the unload station
    '''

    def __init__(self, id):
        self.id = id
        # This list contains the starting times for each truck currently at the station
        self.truck_queue = []
        # The start time of the truck currently unloading at the station
        self.start_time = None
    
        # Variables for tracking unload station statistics throughout the simulation
        self.time_spent_waiting = 0
        self.total_unloads_completed = 0

    def inUse(self):
        return len(self.truck_queue) > 0
    
    def queueTime(self, cur_time):
        if not self.inUse():
            return 0
        return len(self.truck_queue)*const.UNLOAD_TIME - (cur_time - self.start_time)

    def enqueue(self, truck, cur_time):

        self.time_spent_waiting += self.queueTime(cur_time)

        if not self.inUse():
            self.start_time = cur_time
   
        self.truck_queue.append((truck, cur_time))
    
    def startNextUnload(self, cur_time):
        
        self.total_unloads_completed += 1

        self.truck_queue[0][0].total_unloads += 1

        self.truck_queue = self.truck_queue[1:]

        if len(self.truck_queue):
            self.start_time = self.truck_queue[0][1]

        return None
        

class TaskQueue():

    def __init__(self):
        self.queue = []
    
    def enqueue(self, task):
        func, time = task
        i = 0
        while i < len(self.queue):
            if time < self.queue[i][1]:
                break
            elif time == self.queue[i][1] and func.__name__ == 'startNextUnload':
                # We want to make sure we clear 
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
        
        # Return the first station that isn't currently in use
        if not station.inUse():
            return station

        # Calculate the time it would take to unload at a station
        queue_time = station.queueTime(cur_time)
        
        # Find the minimum time it would take to unload at a station in the event all stations are in use
        if not mn or queue_time < mn:
            mn = queue_time
            mnStation = station
    
    return mnStation

def RunSimulation(n, m):
    ''' Runs the simulation of a lunar Helium-3 mining operation. The simulation represents 72 hours of non-stop mining and must execute faster than real-time to provide timely analysis.
        Provides statistics related to truck/unload station performance and efficiency upon simulation completion.

        Args:
            n (int): Number of mining trucks in the simulation.
            m (int): Number of unload stations in the simulation.
    '''

    # Initialize instances of each mining truck/unload station and the task_queue
    task_queue = TaskQueue()
    mining_trucks = [MiningTruck(i+1, task_queue) for i in range(n)]
    unload_stations = [UnloadStation(i+1) for i in range(m)]
    
    while True:
        # Continuously pull the next item from the task queue; each item in the queue is a tuple in the form of (task, time) - time is when the task starts executing
        # No need to worry about the queue being empty, everytime a task is performed, the next task in the mining truck's task flow is added to the queue
        task, time = task_queue.getCurrentTask()
        #print(time, task.__name__, task.__self__.id)

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
    
    # Display statistics of the performance/efficiency of each mining truck and unload station
    print("\nTruck ID | Total Mining Time | Average Mining Time | Total Unloads | Time Spent Waiting")
    print("-"*87)
    for i in sorted(mining_trucks, key=lambda x: x.total_unloads, reverse=True):
        time_spent_mining = "{}h {}".format(str(i.time_spent_mining//3600), datetime.datetime.fromtimestamp(i.time_spent_mining).strftime('%Mm %Ss'))
        time_spent_waiting = "{}h {}".format(str(i.time_spent_waiting//3600), datetime.datetime.fromtimestamp(i.time_spent_waiting).strftime('%Mm %Ss'))
        print("{id:>8d} | {tmt:>17s} | {amt:>19.2f} | {tu:>13d} | {tsw:>18s}".format(id=i.id, tmt=time_spent_mining, amt=i.time_spent_mining/i.total_times_mined, tu=i.total_unloads, tsw=time_spent_waiting))
        

def ParseArgs():
    ''' Parse arguments using the argparse module for the number of mining trucks (n) and number of unload stations (m).
        Both arguments are required and are non-positional, keyword arguments. '''

    parser = argparse.ArgumentParser(description='Get number of mining trucks and unload station')
    parser.add_argument('-n', '--numTrucks', type=int, help='Number of mining trucks', required=True)
    parser.add_argument('-m', '--unloadStations', type=int, help='Number of unload stations', required=True)
    parser.add_argument('--logging', type=bool, help='Whether or not to log the mining truck tasks to a separate log file')
    args = parser.parse_args()
    return args.numTrucks, args.unloadStations


if __name__ == '__main__':
    # Get number of mining trucks (n) and number of unload stations (m)
    n, m = ParseArgs()
    
    RunSimulation(n, m)
