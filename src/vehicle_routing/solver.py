from timefold.solver import SolverManager, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)

from .domain import *
from .constraints import define_constraints


solver_config = SolverConfig(
    solution_class=VehicleRoutePlan,
    entity_class_list=[Vehicle, Visit],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=define_constraints
    ),
    termination_config=TerminationConfig(
        spent_limit=Duration(seconds=30)
    )
)

solver_manager = SolverManager.create(solver_config)
solution_manager = SolutionManager.create(solver_manager)

# import logging

# logging.basicConfig(level=logging.DEBUG)

# def debug_solution(solution):
#     print("\n--- Solution Debugging ---")
#     for vehicle in solution.vehicles:
#         print(f"\n🚗 Vehicle {vehicle.vehicle_id} ({vehicle.vehicle_type}):")
#         for visit in vehicle.visits:
#             print(f" - Visit {visit.id}: {visit.location} at {visit.arrival_time}, Paired Visit: {visit.paired_visit_id}, Vehicle: {visit.vehicle.id if visit.vehicle else 'None'}")

#     print("\n--- Checking Pickup Before Dropoff ---")
#     for visit in solution.visits:
#         if visit.paired_visit_id:
#             paired_visit = next((v for v in solution.visits if v.id == visit.paired_visit_id), None)
#             if paired_visit and visit.arrival_time and paired_visit.arrival_time:
#                 print(f"Pickup {visit.id} at {visit.arrival_time} -> Dropoff {paired_visit.id} at {paired_visit.arrival_time}")
#                 if visit.arrival_time > paired_visit.arrival_time:
#                     print(f"❌ ERROR: Pickup {visit.id} happens after Dropoff {paired_visit.id}!")

# debug_solution(solver_config)