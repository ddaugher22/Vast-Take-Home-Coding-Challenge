import pytest
from simulation import MiningTruck, UnloadStation, TaskQueue

def test_unload_station_queue_time():
    """ Tests that the queue time returned is the correct value """
    task_queue = TaskQueue()
    station = UnloadStation(id=2)
    assert station.inUse() is False
    assert station.queueTime(0) == 0

    truck1 = MiningTruck(1, task_queue)
    
    # Truck will start unloading at this station at 300 seconds into the simulation
    truck1_start_time = 300
    station.enqueue(truck1, truck1_start_time)

    assert station.inUse() is True
    assert station.start_time == truck1_start_time

    # Another truck comes to the station 1 minute after the first truck start unloading; there should still be 4 minutes (240 seconds) left for the first truck
    truck2 = MiningTruck(2, task_queue)
    
    # Truck 2 will attempt to start unloading at this station at 360 seconds into the simulation
    truck2_start_time = 360

    assert station.queueTime(truck2_start_time) == 240 # assert that truck2 has to wait 4 minutes to start unloading

    station.enqueue(truck2, truck2_start_time)

    assert station.inUse() is True
    assert station.start_time == truck1_start_time # start time should not change yet since first truck is still unloading

    # Assume another truck were to come one more minute into the future; there should be 3 minutes left on the first truck and 5 on the second so in total the next truck should have to wait 8 minutes
    assert station.queueTime(truck2_start_time + 60) == 480

def test_task_queue_initialization():
    """ Verify the task queue gets initialized with a mining task for each truck in the simulation """
    
    task_queue = TaskQueue()

    # Setup 5 trucks
    num_trucks = 5
    trucks = [MiningTruck(i+1, task_queue) for i in range(num_trucks)]

    # Verify that there are 5 startMining operations in the task_queue
    assert len(task_queue.queue)==num_trucks
    for item in task_queue.queue:
        task, time = item
        assert task.__name__ == "startMining"
        assert time == 0
    
