import argparse
import random
import datetime
import sys
import constants as const

class MiningTruck():
    """ Represents a mining truck that continuously performs the following work flow:
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
    """

    def __init__(self, id, task_queue):
        """ Initialize a MiningTruck """
        
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
        """ Travel to a mining location from the unload station.

            Args:
                cur_time (int): Time at which the truck begins traveling to the mining location
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        """
        
        self.times_traveled += 1

        return((self.startMining, cur_time + const.TRAVEL_TIME))
    
    def goToUnloadStation(self, cur_time):
        """ Travel to an unload station from the mining location after a mining operation has been completed.

            Args:
                cur_time (int): Time at which the truck begins traveling to the unload station
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        """

        self.times_traveled += 1
        
        return((self.unload, cur_time + const.TRAVEL_TIME))
    
    def startMining(self, cur_time):
        """ Start the mining process for this truck. Mining time is a random time in seconds between 1 and 5 hours.

            Args:
                cur_time (int): Time at which the truck begins the mining operation
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        """

        # Get a random time between 1 and 5 hours in seconds, representing the amount of time this truck will spend mining
        mining_time = random.randint(3600, 18000)
        
        self.time_spent_mining += mining_time
        self.total_times_mined += 1

        return((self.goToUnloadStation, cur_time + mining_time))
    
    def unload(self, cur_time, station):
        """ Start the unloading process of Helium-3 at the specified unload station.

            Args:
                cur_time (int): Time at which the truck begins traveling to the mining location
                station (instance): Instance of the station this truck is currently unloading or waiting to unload at
            Returns:
                tuple (func, int): Tuple containing this truck's next task, and the time the task should be executed. This tuple will be added to the simulation's task queue.
        """

        queue_time = station.queueTime(cur_time)
        self.time_spent_waiting += queue_time
       
        station.enqueue(self, cur_time)
        return (self.goToMiningLocation, cur_time + queue_time)


class UnloadStation():
    """ Represents an unload station where mining trucks unload Helium-3.

        Attributes:
            total_unloads (int): Number of times this truck unloaded it's mined Helium-3 at an unload station
            total_times_mined (int): Number of times this truck mined Helium-3 at a mining location
            time_spent_waiting (int): Total time in seconds this truck spent waiting at an unload station (in the event all stations were in use when the truck arrived)
            time_spent_mining (int): Total time in seconds this truck spent mining at mining locations
            times_traveled (int): Total number of times this truck traveled between mining locations and the unload station
    """

    def __init__(self, id):
        """ Initialize an UnloadStation """

        self.id = id
        # This list contains the starting times for each truck currently at the station
        self.truck_queue = []
        # The start time of the truck currently unloading at the station
        self.start_time = None
    
        # Variables for tracking unload station statistics throughout the simulation
        self.time_spent_waiting = 0
        self.total_unloads = 0
    
    def inUse(self):
        """ Check if this station is occupied by another truck unloading Helium-3.
            
            Returns:
                bool: True if station queue is not empty, False if it is empty
        """

        return len(self.truck_queue) > 0
    
    def queueTime(self, cur_time):
        """ Get the amount of time (in seconds) that the truck would have to wait if it queued at this station
        
            Returns:
                int: the queue time (in seconds) for a truck just arriving at this station
        """
        if not self.inUse():
            return 0
        return len(self.truck_queue)*const.UNLOAD_TIME - (cur_time - self.start_time)

    def enqueue(self, truck, cur_time):
        """ Add truck to the queue for this station. A truck being in the station's queue does not mean it's waiting. The first truck in the queue is the truck currently unloading.

            Args:
                truck (instance): The MiningTruck instance that is queueing up at this unload station.
                cur_time (int): The time (in seconds) at which the truck is queueing up at this station.
        """
        queue_time = self.queueTime(cur_time)
        self.time_spent_waiting += queue_time

        if not self.inUse():
            self.start_time = cur_time
   
        self.truck_queue.append((truck, cur_time+queue_time))
    
    def startNextUnload(self, cur_time):
        """ After the completion of an unload process, start the unload process for the next mining truck in this station's queue.

            Args:
                cur_time (int): The time (in seconds) at which the truck is queueing up at this station.
        """
        
        self.total_unloads += 1

        self.truck_queue[0][0].total_unloads += 1

        self.truck_queue = self.truck_queue[1:]

        if len(self.truck_queue):
            self.start_time = self.truck_queue[0][1]

        return None
        

class TaskQueue():
    """ This class serves as the manager for all tasks performed by mining trucks in this simulation. Tasks are added to the class's queue attribute using self.enqueue. Each item in the queue is a tuples made up of a task (func) and the time (int) at which the task should be performed. The queue is organized by the time in increasing order.

        Attributes:
            total_unloads (int): Number of times this truck unloaded it's mined Helium-3 at an unload station
            total_times_mined (int): Number of times this truck mined Helium-3 at a mining location
            time_spent_waiting (int): Total time in seconds this truck spent waiting at an unload station (in the event all stations were in use when the truck arrived)
            time_spent_mining (int): Total time in seconds this truck spent mining at mining locations
            times_traveled (int): Total number of times this truck traveled between mining locations and the unload station
    """

    def __init__(self):
        """ Initialize a TaskQueue """
        self.queue = []
    
    def enqueue(self, task):
        """ Insert a task into the queue. Tasks are inserted based off the time they will be performed.
           
            Args:
                task (tuple): tuple containing a task(func) and the time the task should be performed (int)
        """

        func, time = task

        # Find the queue index (i) the task should be inserted at
        
        i = 0
        while i < len(self.queue):
            if time < self.queue[i][1]:
                break
            elif time == self.queue[i][1] and func.__name__ == 'startNextUnload':
                # startNextUnload tasks have priority over other tasks with the same time of execution
                # This function clears unload stations of mining trucks that have completed their unload process
                break
            i += 1
        self.queue.insert(i, task)

    def getCurrentTask(self):
        """ Retrieve the next task that should be performed and remove it from the queue.
            No need to worry about the queue being empty and causing an IndexError; trucks always add a new task to the queue when they have completed one.

            Returns:
                tuple(func, int): Tuple containing the next task and it's time
        """
        
        nextTask = self.queue[0]
        self.queue = self.queue[1:]
        return nextTask

def GetNextUnloadStation(stations, cur_time):
    """ Return the unload station with the current lowest waiting time.

        Args:
            stations (list): List of all UnloadStation instances
            cur_time (int): Time (in seconds) at which the truck is trying to unload at a station

        Returns:
            The UnloadStation instance with the current lowest waiting time
    """
    mn = None  # lowest waiting time
    mnStation = None # station with lowest waiting time

    for station in stations:
        
        # Return the first station that isn't currently in use
        if not station.inUse():
            return station

        # Calculate the time it would take to unload at a station
        queue_time = station.queueTime(cur_time)
        
        # Find the minimum time it would take to unload at a station in case all stations are in use
        if not mn or queue_time < mn:
            mn = queue_time
            mnStation = station
    
    # Since loop broke, all stations are currently in use, return the station with the lowest waiting time
    return mnStation

def ParseArgs():
    """ Parse arguments using the argparse module for the number of mining trucks (n) and number of unload stations (m).
        Both arguments are required and are non-positional, keyword arguments. """

    parser = argparse.ArgumentParser(description='Get number of mining trucks and unload station')
    parser.add_argument('-n', '--numTrucks', type=int, help='Number of mining trucks', required=True)
    parser.add_argument('-m', '--unloadStations', type=int, help='Number of unload stations', required=True)
    args = parser.parse_args()
    
    return args.numTrucks, args.unloadStations

def DisplayStatistics(mining_trucks, unload_stations):
    """ Report statistics/efficiency of the mining trucks and unload stations over the course of the simulation. Mining truck statistics are displayed first, followed by unload station statistics.

        Args:
            mining_trucks (list): List of mining truck instances
            unload_stations: (list): List of unload station instances
    """

    # Sort trucks based off the following criteria: most unloads -> lowest average mining time
    trucks_sorted = sorted(mining_trucks, key=lambda x: (x.total_unloads, -x.time_spent_mining/x.total_times_mined), reverse=True)

    # Sort stations based off the following criteria: most unloads -> lowest total waiting time
    stations_sorted = sorted(unload_stations, key=lambda x: (x.total_unloads, -x.time_spent_waiting), reverse=True)


    print("\n---Simulation Complete---\n")

    print("Trucks and stations are sorted by their performance and efficiency.\nFor trucks this is measured by the number of unloads a truck processed over the 72 hours, followed by their average mining time.\nFor stations, this is measured by the number of unloads processed by a station over the 72 hours, followed by the total time trucks spent waiting at the station.\n")
    
    # Display statistics for each mining truck - trucks are sorted by total unloads followed by their average mining time

    print("Mining Truck Performance ({} trucks)".format(len(mining_trucks)))
    print("\nTruck ID | Total Mining Time | Average Mining Time | Total Unloads | Time Spent Waiting")
    print("-"*87)
    
    for truck in trucks_sorted:
        time_spent_mining = "{}h {}".format(str(truck.time_spent_mining//3600), datetime.datetime.fromtimestamp(truck.time_spent_mining).strftime('%Mm %Ss'))
        time_spent_waiting = "{}h {}".format(str(truck.time_spent_waiting//3600), datetime.datetime.fromtimestamp(truck.time_spent_waiting).strftime('%Mm %Ss'))
        
        average_mining_time_secs = truck.time_spent_mining/truck.total_times_mined
        average_mining_time = "{}h {}".format(str(int(average_mining_time_secs//3600)), datetime.datetime.fromtimestamp(average_mining_time_secs).strftime('%Mm %Ss'))

        print("{id:>8d} | {tmt:>17s} | {amt:>19s} | {tu:>13d} | {tsw:>18s}".format(id=truck.id, tmt=time_spent_mining, amt=average_mining_time, tu=truck.total_unloads, tsw=time_spent_waiting))
    
    #Diplay statistics for each unload station - stations are sorted by total unloads followed by total time trucks spent waiting at that station
    
    print("\nUnload Station Performance ({} stations)".format(len(unload_stations)))
    print("\nStation ID | Total Unloads | Total Time Trucks Waited | Avg Waiting Time Per Unload")
    print("-"*83)
    
    for station in stations_sorted:
        time_spent_waiting = "{}h {}".format(str(station.time_spent_waiting//3600), datetime.datetime.fromtimestamp(station.time_spent_waiting).strftime('%Mm %Ss'))
        
        average_waiting_time_secs = 0 if not station.total_unloads else station.time_spent_waiting/station.total_unloads
        average_truck_waiting_time = "{}h {}".format(str(int(average_waiting_time_secs//3600)), datetime.datetime.fromtimestamp(average_waiting_time_secs).strftime('%Mm %Ss'))
        
        print("{id:>10d} | {tup:>13d} | {tttw:>24s} | {atwt:>27s}".format(id=station.id, tup=station.total_unloads, tttw=time_spent_waiting, atwt=average_truck_waiting_time))


def RunSimulation(n, m):
    """ Runs the simulation of a lunar Helium-3 mining operation. The simulation represents 72 hours of non-stop mining and must execute faster than real-time to provide timely analysis.
        Provides statistics related to truck/unload station performance and efficiency upon simulation completion.

        Args:
            n (int): Number of mining trucks in the simulation.
            m (int): Number of unload stations in the simulation.
    """

    # Verify that both the number of trucks and number of stations is greather than zero
    if n < 1 or m < 1:
        print("The number of mining trucks and unload stations must be greater than zero")
        sys.exit()


    # Initialize instances of each mining truck/unload station and the task_queue
    task_queue = TaskQueue()
    mining_trucks = [MiningTruck(i+1, task_queue) for i in range(n)] # instantiating a MiningTruck adds a mining task to the task queue
    unload_stations = [UnloadStation(i+1) for i in range(m)]
    

    # A task is an action that can be performed by a mining truck (mine, unload, travel to station/mine). Each task is represented by a function within the MiningTruck class. These tasks are inserted into a task queue in the form of tuples (task, task time - time task should be performed). The loop below continuously pulls the next task that should be performed and runs the task (function). Each function then returns the next task (tuple) that should be performed by that truck, which is then added back into the queue. The loop breaks when the 72 hour mark has been passed.

    while True:
        task, time = task_queue.getCurrentTask()

        # Verify the simulation time hasn't passed the 72 hour mark; if it does, break
        if time > const.TOTAL_SIM_TIME:
            break

        if task.__name__ == 'unload':
            station = GetNextUnloadStation(unload_stations, time)
            nextTask = task(time, station)
            task_queue.enqueue((station.startNextUnload, time+station.queueTime(time)))
        else:
            nextTask = task(time)

        # Add the truck's next task to the task queue
        if nextTask:
            task_queue.enqueue(nextTask)
    

    # Display statistics of the performance/efficiency of each mining truck and unload station
    DisplayStatistics(mining_trucks, unload_stations)
       


if __name__ == '__main__':
    # Get number of mining trucks (n) and number of unload stations (m)
    n, m = ParseArgs() 
    
    # Run the simulation with the desired number of trucks and stations
    RunSimulation(n, m)
