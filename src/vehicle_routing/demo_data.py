from typing import Generator, TypeVar, Sequence, List
from datetime import date, datetime, time, timedelta
from enum import Enum
from random import Random
from dataclasses import dataclass

import pandas as pd

from .domain import *


FIRST_NAMES = ("Amy", "Beth", "Carl", "Dan", "Elsa", "Flo", "Gus", "Hugo", "Ivy", "Jay")
LAST_NAMES = ("Cole", "Fox", "Green", "Jones", "King", "Li", "Poe", "Rye", "Smith", "Watt")
SERVICE_DURATION_MINUTES = (10, 20, 30, 40)
MORNING_WINDOW_START = time(8, 0)
MORNING_WINDOW_END = time(12, 0)
AFTERNOON_WINDOW_START = time(13, 0)
AFTERNOON_WINDOW_END = time(18, 0)


@dataclass
class _DemoDataProperties:
    seed: int
    visit_count: int
    vehicle_count: int
    vehicle_start_time: time
    min_demand: int
    max_demand: int
    min_vehicle_capacity: int
    max_vehicle_capacity: int
    south_west_corner: Location
    north_east_corner: Location

    def __post_init__(self):
        if self.min_demand < 1:
            raise ValueError(f"minDemand ({self.min_demand}) must be greater than zero.")
        if self.max_demand < 1:
            raise ValueError(f"maxDemand ({self.max_demand}) must be greater than zero.")
        if self.min_demand >= self.max_demand:
            raise ValueError(f"maxDemand ({self.max_demand}) must be greater than minDemand ({self.min_demand}).")
        if self.min_vehicle_capacity < 1:
            raise ValueError(f"Number of minVehicleCapacity ({self.min_vehicle_capacity}) must be greater than zero.")
        if self.max_vehicle_capacity < 1:
            raise ValueError(f"Number of maxVehicleCapacity ({self.max_vehicle_capacity}) must be greater than zero.")
        if self.min_vehicle_capacity >= self.max_vehicle_capacity:
            raise ValueError(f"maxVehicleCapacity ({self.max_vehicle_capacity}) must be greater than "
                             f"minVehicleCapacity ({self.min_vehicle_capacity}).")
        if self.visit_count < 1:
            raise ValueError(f"Number of visitCount ({self.visit_count}) must be greater than zero.")
        if self.vehicle_count < 1:
            raise ValueError(f"Number of vehicleCount ({self.vehicle_count}) must be greater than zero.")
        if self.north_east_corner.latitude <= self.south_west_corner.latitude:
            raise ValueError(f"northEastCorner.getLatitude ({self.north_east_corner.latitude}) must be greater than "
                             f"southWestCorner.getLatitude({self.south_west_corner.latitude}).")
        if self.north_east_corner.longitude <= self.south_west_corner.longitude:
            raise ValueError(f"northEastCorner.getLongitude ({self.north_east_corner.longitude}) must be greater than "
                             f"southWestCorner.getLongitude({self.south_west_corner.longitude}).")


class DemoData(Enum):
    PHILADELPHIA = _DemoDataProperties(0, 55, 6, time(7, 30),
                                       1, 2, 15, 30,
                                       Location(latitude=39.7656099067391,
                                                longitude=-76.83782328143754),
                                       Location(latitude=40.77636644354855,
                                                longitude=-74.9300739430771))

    HARTFORT = _DemoDataProperties(1, 50, 6, time(7, 30),
                                   1, 3, 20, 30,
                                   Location(latitude=41.48366520850297,
                                            longitude=-73.15901689943055),
                                   Location(latitude=41.99512052869307,
                                            longitude=-72.25114548877427))

    FIRENZE = _DemoDataProperties(2, 77, 6, time(7, 30),
                                  1, 2, 20, 40,
                                  Location(latitude=43.751466,
                                           longitude=11.177210),
                                  Location(latitude=43.809291,
                                           longitude=11.290195))


def doubles(random: Random, start: float, end: float) -> Generator[float, None, None]:
    while True:
        yield random.uniform(start, end)


def ints(random: Random, start: int, end: int) -> Generator[int, None, None]:
    while True:
        yield random.randrange(start, end)


T = TypeVar('T')


def values(random: Random, sequence: Sequence[T]) -> Generator[T, None, None]:
    start = 0
    end = len(sequence) - 1
    while True:
        yield sequence[random.randint(start, end)]


def generate_names(random: Random) -> Generator[str, None, None]:
    while True:
        yield f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'


# def generate_demo_data(demo_data_enum: DemoData) -> VehicleRoutePlan:
#     random = Random(demo_data_enum.value.seed)
#     latitudes = doubles(random, demo_data_enum.value.south_west_corner.latitude, demo_data_enum.value.north_east_corner.latitude)
#     longitudes = doubles(random, demo_data_enum.value.south_west_corner.longitude, demo_data_enum.value.north_east_corner.longitude)

#     vehicles_df = pd.read_csv("src/vehicle_routing/data/Vehicles.csv")
#     trips_df = pd.read_csv("src/vehicle_routing/data/Trips_v2.csv")
#     today = datetime.today().date()

#     demands = ints(random, demo_data_enum.value.min_demand, demo_data_enum.value.max_demand + 1)
#     service_durations = values(random, SERVICE_DURATION_MINUTES)
#     vehicle_capacities = ints(random, demo_data_enum.value.min_vehicle_capacity,
#                               demo_data_enum.value.max_vehicle_capacity + 1)

#     VEHICLE_TYPES = ["WC", "CC", "STS"]
#     # vehicle_types = values(random, VEHICLE_TYPES)

#     # vehicles = [Vehicle(
#     #     id=str(i),
#     #     capacity=next(vehicle_capacities),
#     #     home_location=Location(latitude=next(latitudes), longitude=next(longitudes)),
#     #     departure_time=datetime.combine(date.today() + timedelta(days=1), demo_data_enum.value.vehicle_start_time),
#     #     vehicle_type=next(vehicle_types)  # ✅ Assign a vehicle type
#     # ) for i in range(demo_data_enum.value.vehicle_count)]

#     vehicles = [Vehicle(id=str(row["Van_ID"]),
#                     # capacity=next(vehicle_capacities),
#                     capacity=row["TotalCapacity"],
#                     home_location=Location(
#                         latitude=row["Vehicle_Location(Lat, Long)"].split(",")[0],
#                         longitude=row["Vehicle_Location(Lat, Long)"].split(",")[1]),
#                     departure_time=datetime.strptime(row["Vehicle_Start_Time"], "%H:%M").replace(
#                         year=today.year, month=today.month, day=today.day),
#                     # vehicle_type=random.choice(vehicle_type_list)
#                     vehicle_type=row["Vehicle_type"],
#                     )
#             for index, row in vehicles_df.iterrows()]


#     # names = generate_names(random)
#     # visits = []

#     visits: List[Visit] = []
#     visit_map = {}
#     trips_df["Appt Time"] = pd.to_datetime(trips_df["Appt Time"]).dt.strftime("%H:%M:%S")

#     for index, trip in trips_df.iterrows():  # Ensure pairs
#         pickup_id = f"pickup_{index}"
#         dropoff_id = f"dropoff_{index}"
#         trip_vehicle_type = trip["Mobility"]

#         visit_name = trip["name"]
#         pickup_time = datetime.strptime(trip["Pickup Time"], "%H:%M").replace(
#                             year=today.year, month=today.month, day=today.day)
#         dropoff_time = datetime.strptime(trip["Appt Time"], "%H:%M:%S").replace(
#                             year=today.year, month=today.month, day=today.day) - timedelta(minutes=5)
        
#         # pickup_location = Location(latitude=next(latitudes), longitude=next(longitudes))
#         # dropoff_location = Location(latitude=next(latitudes), longitude=next(longitudes))

#         # name = next(names)
#         # pickup_time = datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_START)
#         pickup_visit = Visit(
#             id=pickup_id,
#             name=f"Pickup {visit_name}",
#             location=Location(latitude=trip["PickupLatitude"], longitude=trip["PickupLongitude"]),
#             demand=next(demands),
#             # min_start_time=datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_START),
#             # max_end_time=datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_END),
#             min_start_time=pickup_time,
#             max_end_time=pickup_time + timedelta(minutes=30),
#             service_duration=timedelta(minutes=next(service_durations)),
#             paired_visit_id=dropoff_id,  # ✅ Store drop-off ID instead of full object
#             vehicle_type=trip_vehicle_type,  # ✅ Assign trip a vehicle type
#             is_pickup=True
#         )

#         dropoff_visit = Visit(
#             id=dropoff_id,
#             name=f"Dropoff {visit_name}",
#             location=Location(latitude=trip["DestinationLatitude"], longitude=trip["DestinationLongitude"]),
#             demand=-pickup_visit.demand,  # Drop-off negates pickup demand
#             min_start_time=dropoff_time,  # Ensures drop-off happens later
#             max_end_time=dropoff_time + timedelta(minutes=30),
#             service_duration=timedelta(minutes=next(service_durations)),
#             paired_visit_id=pickup_id,  # ✅ Store pickup ID instead of full object
#             vehicle_type=trip_vehicle_type,  # ✅ Ensure same type as pickup
#             is_dropoff=True
#         )

#         visits.append(pickup_visit)
#         visits.append(dropoff_visit)

#     return VehicleRoutePlan(
#         name="demo",
#         south_west_corner=demo_data_enum.value.south_west_corner,
#         north_east_corner=demo_data_enum.value.north_east_corner,
#         vehicles=vehicles,
#         visits=visits
#     )


def generate_demo_data(demo_data_enum: DemoData) -> VehicleRoutePlan:
    print("demo_data_enum", demo_data_enum)
    random = Random(0)

    # vehicles_df = pd.read_csv("src/vehicle_routing/data/Vehicles.csv")
    # trips_df = pd.read_csv("src/vehicle_routing/data/Trips_v2.csv")
    today = datetime.today().date()

    demands = ints(random, 1, 3 + 1)
    service_durations = values(random, SERVICE_DURATION_MINUTES)

    VEHICLE_TYPES = ["WC", "CC", "STS"]
    vehicle_types = values(random, VEHICLE_TYPES)

    
    vehicles = [Vehicle(id=str(row["VehicleId"]),
                    # capacity=next(vehicle_capacities),
                    capacity=row["TotalCapacity"],
                    home_location=Location(
                        latitude=row["Vehicle_Location_Lat"],
                        longitude=row["Vehicle_Location_Lon"]),
                        # latitude=row["Vehicle_Location(Lat, Long)"].split(",")[0],
                        # longitude=row["Vehicle_Location(Lat, Long)"].split(",")[1]),
                    # departure_time=datetime.strptime(row["Vehicle_Start_Time"], "%H:%M").replace(
                    #     year=today.year, month=today.month, day=today.day),
                    departure_time=datetime.strptime("2025-02-26T07:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                    # vehicle_type=random.choice(vehicle_type_list)
                    # vehicle_type=row["Vehicle_Type"],
                    vehicle_type=next(vehicle_types),
                    make_model=row["Make_Model"],
                    driver_id=row["DriverId"]
                    )
            for index, row in enumerate(demo_data_enum["vehicles"])]


    # names = generate_names(random)
    # visits = []

    visits: List[Visit] = []
    visit_map = {}
    # trips_df["Appt Time"] = pd.to_datetime(trips_df["Appt Time"]).dt.strftime("%H:%M:%S")

    for index, trip in enumerate(demo_data_enum["trips"]):  # Ensure pairs
        trip_id = trip["TblId"]
        pickup_id = f"pickup_{trip_id}"
        dropoff_id = f"dropoff_{trip_id}"
        trip_vehicle_type = trip["Mobility"]

        # visit_name = trip["name"]
        pickup_time = datetime.strptime(trip["PickupTime"], "%Y-%m-%dT%H:%M:%SZ")
        dropoff_time = datetime.strptime(trip["DropTime"], "%Y-%m-%dT%H:%M:%SZ")
        
        # pickup_location = Location(latitude=next(latitudes), longitude=next(longitudes))
        # dropoff_location = Location(latitude=next(latitudes), longitude=next(longitudes))

        # name = next(names)
        # pickup_time = datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_START)
        pickup_visit = Visit(
            id=pickup_id,
            name=f"Pickup {trip_id}",
            trip_id=trip_id,
            location=Location(latitude=trip["PickupLatitude"], longitude=trip["PickupLongitude"]),
            demand=next(demands),
            # min_start_time=datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_START),
            # max_end_time=datetime.combine(date.today() + timedelta(days=1), MORNING_WINDOW_END),
            min_start_time=pickup_time,
            max_end_time=pickup_time + timedelta(minutes=30),
            service_duration=timedelta(minutes=next(service_durations)),
            paired_visit_id=dropoff_id,  # ✅ Store drop-off ID instead of full object
            vehicle_type=trip_vehicle_type,  # ✅ Assign trip a vehicle type
            is_pickup=True
        )

        dropoff_visit = Visit(
            id=dropoff_id,
            name=f"Dropoff {trip_id}",
            trip_id=trip_id,
            location=Location(latitude=trip["DropLatitude"], longitude=trip["DropLongitude"]),
            demand=-pickup_visit.demand,  # Drop-off negates pickup demand
            min_start_time=dropoff_time,  # Ensures drop-off happens later
            max_end_time=dropoff_time + timedelta(minutes=30),
            service_duration=timedelta(minutes=next(service_durations)),
            paired_visit_id=pickup_id,  # ✅ Store pickup ID instead of full object
            vehicle_type=trip_vehicle_type,  # ✅ Ensure same type as pickup
            is_dropoff=True
        )

        visits.append(pickup_visit)
        visits.append(dropoff_visit)

    return VehicleRoutePlan(
        name="demo",
        south_west_corner=Location(latitude=41.48366520850297,
                                            longitude=-73.15901689943055),
        north_east_corner=Location(latitude=41.99512052869307,
                                            longitude=-72.25114548877427),
        vehicles=vehicles,
        visits=visits
    )


def tomorrow_at(local_time: time) -> datetime:
    return datetime.combine(date.today(), local_time)
