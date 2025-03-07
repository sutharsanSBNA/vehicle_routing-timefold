from timefold.solver import SolverFactory
from datetime import datetime, timedelta
from typing import List, Optional
import json

# ---- Location Class ----
class Location:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
    
    def driving_time_to(self, other_location) -> int:
        # Mock function for travel time (in seconds)
        return int(((abs(self.latitude - other_location.latitude) + abs(self.longitude - other_location.longitude)) * 60) * 10)

# ---- Trip (Pickup & Drop-off) ----
class Trip:
    def __init__(self, trip_id: int, pickup: Location, dropoff: Location, earliest_pickup: datetime, latest_pickup: datetime, 
                 earliest_dropoff: datetime, latest_dropoff: datetime):
        self.trip_id = trip_id
        self.pickup = pickup
        self.dropoff = dropoff
        self.earliest_pickup = earliest_pickup
        self.latest_pickup = latest_pickup
        self.earliest_dropoff = earliest_dropoff
        self.latest_dropoff = latest_dropoff
        self.vehicle = None  # Assigned vehicle
        self.previous_trip: Optional['Trip'] = None  # Previous trip in route

    def arrival_time(self):
        if self.previous_trip:
            return self.previous_trip.departure_time() + timedelta(seconds=self.previous_trip.dropoff.driving_time_to(self.pickup))
        return None

    def departure_time(self):
        if self.arrival_time():
            return self.arrival_time() + timedelta(minutes=5)  # Assume fixed service time
        return None

# ---- Vehicle ----
class Vehicle:
    def __init__(self, vehicle_id: int, home_location: Location, capacity: int):
        self.vehicle_id = vehicle_id
        self.home_location = home_location
        self.capacity = capacity

# ---- Solution Class ----
class VehicleRoutePlan:
    def __init__(self, trips: List[Trip], vehicles: List[Vehicle]):
        self.trips = trips
        self.vehicles = vehicles
        self.score = None

# ---- Running the Solver ----
def solve_vrp(trips: List[Trip], vehicles: List[Vehicle]):
    solver_factory = SolverFactory.create("solverConfig.yaml")  # Ensure this file exists and is correctly configured
    solver = solver_factory.build_solver()
    
    solution = solver.solve(VehicleRoutePlan(trips, vehicles))
    
    # Save output data
    output_data = {
        "trips": [{"trip_id": trip.trip_id, "vehicle_id": trip.vehicle.vehicle_id if trip.vehicle else None} for trip in solution.trips],
        "score": str(solution.score)
    }
    
    with open("vrp_solution.json", "w") as f:
        json.dump(output_data, f, indent=4)
    
    return solution

# ---- Demo Data ----
if __name__ == "__main__":
    home = Location(37.7749, -122.4194)
    
    trips = [
        Trip(1, Location(37.7750, -122.4183), Location(37.7760, -122.4172), datetime.now(), datetime.now() + timedelta(minutes=15), datetime.now() + timedelta(minutes=20), datetime.now() + timedelta(minutes=40)),
        Trip(2, Location(37.7761, -122.4161), Location(37.7770, -122.4150), datetime.now(), datetime.now() + timedelta(minutes=10), datetime.now() + timedelta(minutes=25), datetime.now() + timedelta(minutes=45))
    ]
    
    vehicles = [
        Vehicle(1, home, 4),
        Vehicle(2, home, 4)
    ]
    
    solve_vrp(trips, vehicles)
