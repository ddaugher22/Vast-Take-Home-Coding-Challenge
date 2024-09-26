import pytest
from simulation import MiningTruck, UnloadStation, TaskQueue

def test_mining_truck_initialization():
    """Test that a MiningTruck is initialized with correct attributes."""
    test_queue = TaskQueue()
    truck = MiningTruck(1, test_queue)
    assert truck.id == 1
    assert truck.total_unloads == 0
    assert truck.total_times_mined == 0
    assert truck.time_spent_waiting == 0
    assert truck.time_spent_mining == 0
    assert truck.times_traveled == 0

def test_unload_station_initialization():
    """Test that an UnloadStation is initialized with correct attributes. Verify station is not in use."""
    station = UnloadStation(id=1)
    assert station.id == 1
    assert station.truck_queue == []
    assert station.start_time == None
    assert station.time_spent_waiting == 0
    assert station.total_unloads == 0
    assert station.inUse() is False

