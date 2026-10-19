"""Synthetic home-to-station routing model for the MoveAI prototype.

Distances use Manhattan distance over illustrative coordinates, scaled by 1.2
synthetic km per coordinate unit. A configurable constant speed converts those
distances to synthetic minutes; neither represents a real road network.
"""
from __future__ import annotations

import random
import math
from collections import Counter
from collections.abc import Mapping
from decimal import Decimal
from numbers import Integral, Real
from typing import Any

NODES = {
    "Transit Station": (3.0, 3.0), "North Homes": (2.4, 5.2),
    "East Homes": (5.4, 3.8), "South Homes": (3.5, 0.9),
    "West Homes": (0.8, 2.8), "Park Residences": (4.8, 5.5),
    "Lake Residences": (0.8, 5.0), "Central Residences": (3.5, 4.2),
}
SYNTHETIC_SPEED_KMH = 24.0


def distance(a: str, b: str) -> float:
    """Synthetic Manhattan distance proxy (km), rounded to 2 decimals."""
    ax, ay = NODES[a]
    bx, by = NODES[b]
    return round((abs(ax - bx) + abs(ay - by)) * 1.2, 2)


def travel_minutes(km: float) -> float:
    return km / SYNTHETIC_SPEED_KMH * 60


def _finite_nonnegative_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise ValueError(f"{label} must be a finite non-negative numeric value")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a finite non-negative numeric value") from None
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{label} must be a finite non-negative numeric value")
    return result


def _positive_integer(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a positive integer")
    if isinstance(value, Integral):
        if value <= 0:
            raise ValueError(f"{label} must be a positive integer")
        return int(value)
    if not isinstance(value, (Real, Decimal)):
        raise ValueError(f"{label} must be a positive integer")
    try:
        numeric_value = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a positive integer") from None
    if not math.isfinite(numeric_value) or numeric_value <= 0 or not numeric_value.is_integer():
        raise ValueError(f"{label} must be a positive integer")
    return int(value)


def make_requests(n: int, seed: int, peak: int = 35) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    homes = [name for name in NODES if name != "Transit Station"]
    base = 7 * 60 + 30
    requests = []
    for i in range(n):
        depart = base + rng.randint(0, peak)
        requests.append({"request_id": f"R{i+1:03d}", "pickup": rng.choice(homes),
                         "destination": "Transit Station", "departure_min": depart,
                         "passengers": rng.choice([1, 1, 1, 2]), "max_wait_min": 10})
    return sorted(requests, key=lambda r: (r["departure_min"], r["request_id"]))


def _validate_requests(requests: list[dict[str, Any]], boundary: str) -> list[dict[str, Any]]:
    """Validate the shared request schema without coercing malformed values."""
    if not isinstance(requests, (list, tuple)):
        raise ValueError(f"{boundary}: requests must be a list or tuple")
    required = {"request_id", "pickup", "destination", "departure_min", "passengers", "max_wait_min"}
    records = []
    seen_ids = set()
    for index, request in enumerate(requests):
        label = f"{boundary}: request at index {index}"
        if not isinstance(request, Mapping):
            raise ValueError(f"{label} must be a mapping")
        missing = required - request.keys()
        if missing:
            raise ValueError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
        request_id = request["request_id"]
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError(f"{label} request_id must be a non-empty string")
        if request_id in seen_ids:
            raise ValueError(f"{boundary}: duplicate request_id {request_id!r}")
        seen_ids.add(request_id)
        for field in ("pickup", "destination"):
            node = request[field]
            if not isinstance(node, str) or node not in NODES:
                raise ValueError(f"{label} has unknown {field} node {node!r}")
        if request["destination"] != "Transit Station":
            raise ValueError(f"{label} destination must be 'Transit Station'")
        passengers = request["passengers"]
        _positive_integer(passengers, f"{label} passengers")
        for field, minimum in (("departure_min", None), ("max_wait_min", 0)):
            value = request[field]
            try:
                finite_numeric = (isinstance(value, (Real, Decimal)) and
                                  not isinstance(value, bool) and math.isfinite(float(value)))
            except (OverflowError, ValueError):
                finite_numeric = False
            if not finite_numeric:
                raise ValueError(f"{label} {field} must be a finite numeric value")
            if minimum is not None and value < minimum:
                raise ValueError(f"{label} {field} must be non-negative")
        records.append(dict(request))
    return records


def _route_stats(group: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate an ordered route; pickup time is request time or vehicle arrival."""
    if not group:
        return {"feasible": False, "reason": "empty route"}
    route_km = 0.0
    elapsed_to_pickup = 0.0
    current = group[0]["pickup"]
    clock = float(group[0]["departure_min"])
    pickups, waits = [], {}
    for r in group:
        leg = distance(current, r["pickup"])
        route_km += leg
        clock += travel_minutes(leg)
        clock = max(clock, float(r["departure_min"]))
        wait = clock - float(r["departure_min"])
        waits[r["request_id"]] = wait
        pickups.append(clock)
        current = r["pickup"]
    for r in group:
        leg = distance(current, "Transit Station")
        route_km += leg
        current = "Transit Station"
    # Each passenger rides from their pickup through every later pickup to station.
    passenger_detours = {}
    for i, r in enumerate(group):
        ride_km = sum(distance(group[j]["pickup"], group[j + 1]["pickup"])
                      for j in range(i, len(group) - 1))
        ride_km += distance(group[-1]["pickup"], "Transit Station")
        passenger_detours[r["request_id"]] = max(
            0.0, round(ride_km - distance(r["pickup"], "Transit Station"), 2))
    return {"feasible": True, "vehicle_km": round(route_km, 2), "waits": waits,
            "detours": passenger_detours, "pickup_times": pickups}


def plan_routes(requests: list[dict[str, Any]], capacity: int = 6,
                time_window: float = 8, max_detour_km: float = 2.5) -> dict[str, Any]:
    """Deterministic greedy grouping with whole-route capacity, wait, and detour checks.

    Requests are considered in departure order; feasible candidates are attempted
    by proximity to the route's first pickup. This is a heuristic, not an optimum.
    """
    records = _validate_requests(requests, "plan_routes")
    capacity = _positive_integer(capacity, "capacity")
    time_window = _finite_nonnegative_number(time_window, "time_window")
    max_detour_km = _finite_nonnegative_number(max_detour_km, "max_detour_km")
    remaining = sorted(records, key=lambda r: (float(r["departure_min"]), r["request_id"]))
    routes, unserved = [], []
    while remaining:
        seed = remaining.pop(0)
        if int(seed["passengers"]) > capacity:
            unserved.append({"request": seed, "reason": "request exceeds vehicle capacity"})
            continue
        group = [seed]
        candidates = sorted(remaining, key=lambda r: (
            distance(seed["pickup"], r["pickup"]), float(r["departure_min"]), r["request_id"]))
        for candidate in candidates:
            trial = sorted(group + [candidate], key=lambda r: (float(r["departure_min"]), r["request_id"]))
            if sum(int(r["passengers"]) for r in trial) > capacity:
                continue
            times = [float(r["departure_min"]) for r in trial]
            if max(times) - min(times) > time_window + 1e-9:
                continue
            stats = _route_stats(trial)
            if any(stats["waits"][r["request_id"]] > float(r["max_wait_min"]) + 1e-9
                   for r in trial):
                continue
            if any(detour > max_detour_km for detour in stats["detours"].values()):
                continue
            group = trial
        used = {r["request_id"] for r in group}
        remaining = [r for r in remaining if r["request_id"] not in used]
        stats = _route_stats(group)
        routes.append({"route_id": f"V{len(routes)+1:02d}", "requests": group,
                       "passengers": sum(int(r["passengers"]) for r in group),
                       "capacity": capacity, "stops": [r["pickup"] for r in group] + ["Transit Station"],
                       **stats})
    # Explain the first relevant reason each unserved request could not be grouped.
    assigned = {r["request_id"] for route in routes for r in route["requests"]}
    for r in records:
        if r["request_id"] in assigned or any(x["request"]["request_id"] == r["request_id"] for x in unserved):
            continue
        compatible = [x for route in routes for x in route["requests"]
                      if abs(float(x["departure_min"])-float(r["departure_min"])) <= time_window + 1e-9]
        reason = "no feasible compatible route; served individually"
        if compatible:
            reason = "capacity, pickup-wait, or passenger-detour constraint"
        unserved.append({"request": r, "reason": reason})
    return {"routes": routes, "unserved": unserved, "served_ids": assigned}


def baseline(requests: list[dict[str, Any]], capacity: int = 6) -> dict[str, Any]:
    """Fair one-vehicle-per-request baseline under the same synthetic distances."""
    requests = _validate_requests(requests, "baseline")
    capacity = _positive_integer(capacity, "capacity")
    routes = []
    unserved = []
    for i, r in enumerate(requests, 1):
        feasible = int(r["passengers"]) <= capacity
        if not feasible:
            unserved.append({"request": r, "reason": "request exceeds vehicle capacity"})
            continue
        routes.append({"route_id": f"B{i:02d}", "requests": [r],
                       "passengers": int(r["passengers"]),
                       "capacity": capacity, "stops": [r["pickup"], "Transit Station"],
                       "vehicle_km": distance(r["pickup"], "Transit Station"),
                       "waits": {r["request_id"]: 0.0},
                       "detours": {r["request_id"]: 0.0}})
    return {"routes": routes, "unserved": unserved}


def metrics(requests: list[dict[str, Any]], routes: list[dict[str, Any]],
            unserved: list[Any], capacity: int) -> dict[str, Any]:
    requests = _validate_requests(requests, "metrics")
    capacity = _positive_integer(capacity, "capacity")
    request_by_id = {r["request_id"]: r for r in requests}
    if not isinstance(routes, (list, tuple)):
        raise ValueError("metrics: routes must be a list or tuple")
    if not isinstance(unserved, (list, tuple)):
        raise ValueError("metrics: unserved must be a list or tuple")

    served_ids = []
    validated_routes = []
    for route_index, route in enumerate(routes):
        if not isinstance(route, Mapping) or not isinstance(route.get("requests"), (list, tuple)):
            raise ValueError(f"metrics: route at index {route_index} must contain a requests list")
        route_label = f"metrics: route at index {route_index}"
        if not route["requests"]:
            raise ValueError(f"{route_label} is empty; empty routes are not allowed")
        if "vehicle_km" not in route or "passengers" not in route:
            raise ValueError(f"{route_label} requires vehicle_km and passengers")
        route_km = _finite_nonnegative_number(route["vehicle_km"], f"{route_label} vehicle_km")
        route_request_ids = []
        for request in route["requests"]:
            if not isinstance(request, Mapping) or not isinstance(request.get("request_id"), str):
                raise ValueError(f"{route_label} contains a request without a valid request_id")
            route_request_ids.append(request["request_id"])
        unknown_route_ids = set(route_request_ids) - set(request_by_id)
        if unknown_route_ids:
            raise ValueError(f"metrics: unknown request IDs in routes: {sorted(unknown_route_ids)}")
        route_passengers = route["passengers"]
        route_passengers = _positive_integer(route_passengers, f"{route_label} passengers")
        expected_passengers = sum(int(request_by_id[rid]["passengers"]) for rid in route_request_ids)
        if route_passengers != expected_passengers:
            raise ValueError(f"{route_label} passengers must equal the sum of assigned request passengers")
        route_capacity = (_positive_integer(route["capacity"], f"{route_label} capacity")
                          if "capacity" in route else capacity)
        if route_passengers > route_capacity:
            raise ValueError(f"{route_label} passengers exceed route capacity")
        wait_map = route.get("waits")
        detour_map = route.get("detours")
        if not isinstance(wait_map, Mapping) or not isinstance(detour_map, Mapping):
            raise ValueError(f"{route_label} requires waits and detours mappings")
        route_id_set = set(route_request_ids)
        for field, values in (("waits", wait_map), ("detours", detour_map)):
            unknown_values = set(values) - route_id_set
            missing_values = route_id_set - set(values)
            if unknown_values:
                raise ValueError(f"{route_label} {field} entries must reference assigned request IDs only")
            if missing_values:
                raise ValueError(f"{route_label} {field} must include every assigned request ID")
            for request_id, value in values.items():
                _finite_nonnegative_number(value, f"{route_label} {field}[{request_id!r}]")
        served_ids.extend(route_request_ids)
        validated_routes.append({**route, "vehicle_km": route_km,
                                 "passengers": int(route_passengers), "capacity": route_capacity})

    unserved_ids = []
    for index, entry in enumerate(unserved):
        request = entry.get("request") if isinstance(entry, Mapping) and "request" in entry else entry
        if not isinstance(request, Mapping) or not isinstance(request.get("request_id"), str):
            raise ValueError(f"metrics: unserved entry at index {index} must contain a valid request_id")
        unserved_ids.append(request["request_id"])

    input_ids = set(request_by_id)
    assigned_ids = set(served_ids)
    unserved_id_set = set(unserved_ids)
    unknown_ids = (assigned_ids | unserved_id_set) - input_ids
    if unknown_ids:
        raise ValueError(f"metrics: unknown request IDs in routes or unserved: {sorted(unknown_ids)}")
    duplicate_ids = [request_id for request_id, count in Counter(served_ids + unserved_ids).items() if count > 1]
    if duplicate_ids:
        raise ValueError(f"metrics: duplicate request assignments: {sorted(duplicate_ids)}")
    missing_ids = input_ids - (assigned_ids | unserved_id_set)
    if missing_ids:
        raise ValueError(f"metrics: requests missing from routes and unserved: {sorted(missing_ids)}")

    served_id_set = assigned_ids
    waits = [(v, int(request_by_id[rid]["passengers"]))
             for route in validated_routes for rid, v in route["waits"].items()]
    detours = [(v, int(request_by_id[rid]["passengers"]))
               for route in validated_routes for rid, v in route["detours"].items()]
    passenger_count = sum(weight for _, weight in waits)
    passenger_km = sum(route["passengers"] * route["vehicle_km"] for route in validated_routes)
    capacity_seat_km = sum(route["capacity"] * route["vehicle_km"]
                           for route in validated_routes)
    return {"vehicle_km": round(sum(r["vehicle_km"] for r in validated_routes), 2),
            "routes": len(validated_routes), "served": len(served_id_set),
            "unserved": len(unserved_id_set),
            "total_wait_min": round(sum(value * weight for value, weight in waits), 2),
            "average_wait_min": round(sum(value * weight for value, weight in waits) / passenger_count, 2) if passenger_count else 0.0,
            "average_detour_km": round(sum(value * weight for value, weight in detours) / sum(weight for _, weight in detours), 2) if detours else 0.0,
            "occupancy_pct": round(passenger_km / capacity_seat_km * 100, 2)
            if capacity_seat_km else 0.0}
