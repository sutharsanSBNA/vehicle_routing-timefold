from timefold.solver.score import ConstraintFactory, HardSoftScore, constraint_provider

from .domain import *

VEHICLE_CAPACITY = "vehicleCapacity"
MINIMIZE_TRAVEL_TIME = "minimizeTravelTime"
SERVICE_FINISHED_AFTER_MAX_END_TIME = "serviceFinishedAfterMaxEndTime"


@constraint_provider
def define_constraints(factory: ConstraintFactory):
    return [
        # Hard constraints
        vehicle_capacity(factory),
        # balance_vehicle_load(factory),
        # service_finished_after_max_end_time(factory),
        pickup_and_dropoff_same_vehicle(factory),
        pickup_before_dropoff(factory),
        match_vehicle_type(factory),
        # enforce_on_time_dropoff(factory),  # ✅ Ensure drop-offs happen on time
        # enforce_no_early_pickup(factory),  # ✅ Prevent pickups from being too early,
        # prioritize_dropoff_before_new_pickup(factory),
        enforce_valid_arrival_time(factory),
        pickup_immediately_before_dropoff(factory) ,

        # force_dropoff_after_pickup(factory),
        use_more_vehicles(factory),
        # Soft constraints
        minimize_travel_time(factory)
    ]

##############################################
# Hard constraints
##############################################

def pickup_immediately_before_dropoff(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  # ✅ Match pickup to drop-off
            .filter(lambda visit, paired: visit.vehicle is not None and paired.vehicle is not None)  # ✅ Ensure both visits have assigned vehicles
            .filter(lambda visit, paired: visit.vehicle.id == paired.vehicle.id)  # ✅ Ensure same vehicle
            .filter(lambda visit, paired: visit.next_visit is not None)  # ✅ Ensure there's a next visit
            .filter(lambda visit, paired: visit.next_visit.id != paired.id)  # ❌ Ensure the next visit is the correct drop-off
            .penalize(HardSoftScore.ONE_HARD, lambda visit, paired: 100_000)  # ✅ Extreme penalty
            .as_constraint("pickupImmediatelyBeforeDropoff"))


def use_more_vehicles(factory: ConstraintFactory):
    return (factory.for_each(Vehicle)
            .filter(lambda vehicle: len(vehicle.visits) == 0)  # ✅ Penalize empty vehicles
            .penalize(HardSoftScore.of(500, 0), lambda vehicle: 1)  # ✅ Stronger incentive to use more vehicles
            .as_constraint("useMoreVehicles"))


def vehicle_capacity(factory: ConstraintFactory):
    return (factory.for_each(Vehicle)
            .filter(lambda vehicle: vehicle.calculate_total_demand() > vehicle.capacity)
            .penalize(HardSoftScore.ONE_HARD,
                      lambda vehicle: vehicle.calculate_total_demand() - vehicle.capacity)
            .as_constraint(VEHICLE_CAPACITY)
            )


def service_finished_after_max_end_time(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.is_service_finished_after_max_end_time())
            .penalize(HardSoftScore.ONE_HARD,
                      lambda visit: visit.service_finished_delay_in_minutes())
            .as_constraint(SERVICE_FINISHED_AFTER_MAX_END_TIME)
            )

from timefold.solver.score import Joiners  # ✅ Import Joiners

# def pickup_before_dropoff(factory: ConstraintFactory):
#     return (factory.for_each(Visit)
#             .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))
#             .filter(lambda visit, paired: visit.arrival_time is not None and paired.arrival_time is not None)
#             .filter(lambda visit, paired: visit.arrival_time > paired.arrival_time)  # ✅ Enforce sequence strictly
#             .penalize(HardSoftScore.of(1000, 0), lambda visit, paired: 1)  # ✅ Increase penalty to 500
#             .as_constraint("pickupBeforeDropoff"))

# def pickup_before_dropoff(factory: ConstraintFactory):
#     return (factory.for_each(Visit)
#             .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  
#             .filter(lambda visit, paired: visit.previous_visit is not None and visit.previous_visit.id == paired.id)  # ✅ Compare IDs, not objects
#             .penalize(HardSoftScore.ONE_HARD, lambda visit, paired: 100_000)  # ✅ Extreme penalty
#             .as_constraint("pickupBeforeDropoff"))

def pickup_before_dropoff(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  
            .filter(lambda visit, paired: visit.vehicle is not None and paired.vehicle is not None)  # ✅ Ensure both visits have a vehicle
            .filter(lambda visit, paired: visit.vehicle.id == paired.vehicle.id)  # ✅ Ensure same vehicle
            .filter(lambda visit, paired: visit.is_pickup and paired.is_dropoff)  # ✅ Ensure correct visit types
            .filter(lambda visit, paired: is_dropoff_before_pickup(visit, paired))  # ❌ Drop-off appears before pickup
            .penalize(HardSoftScore.ONE_HARD, lambda visit, paired: 100_000)  # ✅ Extreme penalty
            .as_constraint("pickupBeforeDropoff"))


def is_dropoff_before_pickup(pickup: Visit, dropoff: Visit) -> bool:
    """Check if the drop-off appears before the pickup in the visit chain."""
    current = dropoff.previous_visit  # Start from drop-off and move backward
    while current is not None:
        if current.id == pickup.id:
            return False  # ✅ Pickup is before drop-off (correct order)
        current = current.previous_visit  # Move backward in the chain
    return True  # ❌ Drop-off was found before pickup (incorrect)


def force_dropoff_after_pickup(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  
            .filter(lambda visit, paired: visit.previous_visit is not None and visit.previous_visit.id != paired.id)  # ✅ Compare IDs, not objects
            .penalize(HardSoftScore.ONE_HARD, lambda visit, paired: 50_000)  # ✅ Strong penalty
            .as_constraint("forceDropoffAfterPickup"))


# def pickup_and_dropoff_same_vehicle(factory: ConstraintFactory):
#     return (factory.for_each(Visit)
#             .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  # ✅ Match pickup to drop-off
#             .filter(lambda visit, paired: visit.vehicle is not None and paired.vehicle is not None)  # ✅ Ensure both visits have assigned vehicles
#             .filter(lambda visit, paired: visit.vehicle.id != paired.vehicle.id)  # ✅ Check if vehicles are different
#             .penalize(HardSoftScore.of(1000, 0), lambda visit, paired: 1)  # ✅ Stronger penalty (1000)
#             .as_constraint("pickupAndDropoffSameVehicle"))

def pickup_and_dropoff_same_vehicle(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .join(Visit, Joiners.equal(lambda visit: visit.paired_visit_id, lambda paired: paired.id))  # ✅ Match pickup to drop-off
            .filter(lambda visit, paired: visit.vehicle is not None and paired.vehicle is not None)  # ✅ Ensure both visits have assigned vehicles
            .filter(lambda visit, paired: visit.vehicle.id != paired.vehicle.id)  # ❌ If vehicles are different, apply penalty
            .penalize(HardSoftScore.ONE_HARD, lambda visit, paired: 100_000)  # ✅ Extreme penalty to block incorrect assignments
            .as_constraint("pickupAndDropoffSameVehicle"))


def match_vehicle_type(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.vehicle is not None)  # ✅ Ensure visit has an assigned vehicle
            .filter(lambda visit: visit.vehicle.vehicle_type != visit.vehicle_type)  # ✅ Check if types mismatch
            .penalize(HardSoftScore.of(10_000, 0), lambda visit: 1)  # ✅ Penalize mismatched vehicle types
            .as_constraint("vehicleTypeConstraint"))


def enforce_on_time_dropoff(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.paired_visit_id is not None)  # ✅ Only for drop-offs
            .filter(lambda visit: visit.arrival_time is not None)
            .filter(lambda visit: visit.arrival_time != visit.min_start_time)  # ✅ Penalize if drop-off is not exactly on time
            .penalize(HardSoftScore.ONE_HARD, lambda visit: abs((visit.arrival_time - visit.min_start_time).seconds // 60))  # ✅ Penalize per minute of deviation
            .as_constraint("onTimeDropoff"))

def enforce_no_early_pickup(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.paired_visit_id is not None)  # ✅ Only for pickups
            .filter(lambda visit: visit.arrival_time is not None)
            .filter(lambda visit: visit.arrival_time < visit.min_start_time)  # ✅ Penalize early pickups
            .penalize(HardSoftScore.ONE_HARD, lambda visit: (visit.min_start_time - visit.arrival_time).seconds // 60)  # ✅ Penalize per minute
            .as_constraint("noEarlyPickup"))


def enforce_exact_dropoff_time(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.paired_visit_id is not None)  # ✅ Only for drop-offs
            .filter(lambda visit: visit.arrival_time is not None and visit.arrival_time != visit.min_start_time)  # ✅ Penalize if drop-off is not exactly on time
            .penalize(HardSoftScore.ONE_HARD, lambda visit: abs((visit.arrival_time - visit.min_start_time).seconds // 60))  # ✅ Penalize per minute of deviation
            .as_constraint("exactDropoffTime"))



def prioritize_dropoff_before_new_pickup(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .join(Visit, Joiners.equal(lambda visit: visit.vehicle, lambda next_visit: next_visit.vehicle))  # ✅ Ensure both visits are on the same vehicle
            .filter(lambda visit, next_visit: visit.paired_visit_id is not None and next_visit.paired_visit_id is None)  # ✅ Ensure visit is a drop-off & next is a pickup
            .filter(lambda visit, next_visit: visit.arrival_time is not None and next_visit.arrival_time is not None)
            .filter(lambda visit, next_visit: visit.arrival_time > next_visit.arrival_time)  # ✅ Penalize if a pickup happens before a drop-off
            .penalize(HardSoftScore.of(1000, 0), lambda visit, next_visit: 1)  # ✅ Strong penalty for wrong order
            .as_constraint("prioritizeDropoffBeforeNewPickup"))


def balance_vehicle_load(factory: ConstraintFactory):
    return (factory.for_each(Vehicle)
            .penalize(HardSoftScore.ONE_SOFT, lambda vehicle: len(vehicle.visits) ** 2)  # ✅ Penalize overloading a single vehicle
            .as_constraint("balanceVehicleLoad"))

# def enforce_valid_arrival_time(factory: ConstraintFactory):
#     return (factory.for_each(Visit)
#             .filter(lambda visit: visit.arrival_time is not None)  # ✅ Ensure visit has an assigned arrival time
#             .filter(lambda visit: visit.arrival_time < visit.min_start_time or visit.arrival_time > visit.max_end_time)  # ❌ Arrival time outside range
#             .penalize(HardSoftScore.ONE_SOFT, lambda visit: abs((visit.arrival_time - visit.min_start_time).seconds // 60) if visit.arrival_time < visit.min_start_time 
#                       else abs((visit.arrival_time - visit.max_end_time).seconds // 60))  # ✅ Soft penalty for small violations
#             .as_constraint("enforceValidArrivalTime"))

def enforce_valid_arrival_time(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.arrival_time is not None and visit.min_start_time is not None and visit.max_end_time is not None)  # ✅ Ensure valid time range
            .filter(lambda visit: visit.arrival_time < visit.min_start_time or visit.arrival_time > visit.max_end_time)  # ❌ Arrival time outside range
            .penalize(HardSoftScore.ONE_HARD,  
                      lambda visit: 10_000 if abs((visit.arrival_time - visit.min_start_time).seconds // 60) > 10 
                      else 100 * abs((visit.arrival_time - visit.min_start_time).seconds // 60))  # ✅ Hard penalty for extreme violations, soft for small ones
            .as_constraint("enforceValidArrivalTime"))


##############################################
# Soft constraints
##############################################


# def minimize_travel_time(factory: ConstraintFactory):
#     return (
#         factory.for_each(Vehicle)
#         .penalize(HardSoftScore.ONE_SOFT,
#                   lambda vehicle: vehicle.calculate_total_driving_time_seconds())
#         .as_constraint(MINIMIZE_TRAVEL_TIME)
#     )
def minimize_travel_time(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.previous_visit is not None)
            .reward(HardSoftScore.ONE_SOFT, lambda visit: max(1, visit.previous_visit.location.driving_time_to(visit.location)))  # ✅ Ensure positive impact
            .as_constraint("minimizeTravelTime"))

