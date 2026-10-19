"""Synthetic home-to-station routing model for the MoveAI prototype.

Distances use Manhattan distance over illustrative coordinates, scaled by 1.2
synthetic km per coordinate unit. A configurable constant speed converts those
distances to synthetic minutes; neither represents a real road network.
"""
from __future__ import annotations

import random
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
                time_window: int = 8, max_detour_km: float = 2.5) -> dict[str, Any]:
    """Deterministic greedy grouping with whole-route capacity, wait, and detour checks.

    Requests are considered in departure order; feasible candidates are attempted
    by proximity to the route's first pickup. This is a heuristic, not an optimum.
    """
    records = [dict(r) for r in requests]
    ids = [r["request_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("request_id values must be unique")
    if capacity < 1 or time_window < 0 or max_detour_km < 0:
        raise ValueError("capacity must be positive and constraints non-negative")
    remaining = sorted(records, key=lambda r: (r["departure_min"], r["request_id"]))
    routes, unserved = [], []
    while remaining:
        seed = remaining.pop(0)
        if int(seed["passengers"]) > capacity:
            unserved.append({"request": seed, "reason": "request exceeds vehicle capacity"})
            continue
        group = [seed]
        candidates = sorted(remaining, key=lambda r: (
            distance(seed["pickup"], r["pickup"]), r["departure_min"], r["request_id"]))
        for candidate in candidates:
            trial = sorted(group + [candidate], key=lambda r: (r["departure_min"], r["request_id"]))
            if sum(int(r["passengers"]) for r in trial) > capacity:
                continue
            times = [int(r["departure_min"]) for r in trial]
            if max(times) - min(times) > time_window:
                continue
            stats = _route_stats(trial)
            if any(stats["waits"][r["request_id"]] > float(r["max_wait_min"]) for r in trial):
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
                      if abs(int(x["departure_min"])-int(r["departure_min"])) <= time_window]
        reason = "no feasible compatible route; served individually"
        if compatible:
            reason = "capacity, pickup-wait, or passenger-detour constraint"
        unserved.append({"request": r, "reason": reason})
    return {"routes": routes, "unserved": unserved, "served_ids": assigned}


def baseline(requests: list[dict[str, Any]], capacity: int = 6) -> dict[str, Any]:
    """Fair one-vehicle-per-request baseline under the same synthetic distances."""
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
    served_ids = {r["request_id"] for route in routes for r in route["requests"]}
    request_by_id = {r["request_id"]: r for r in requests}
    waits = [(v, int(request_by_id[rid]["passengers"]))
             for route in routes for rid, v in route.get("waits", {}).items()]
    detours = [(v, int(request_by_id[rid]["passengers"]))
               for route in routes for rid, v in route.get("detours", {}).items()]
    passenger_count = sum(weight for _, weight in waits)
    seat_km = sum(route["passengers"] * route["vehicle_km"] for route in routes)
    return {"vehicle_km": round(sum(r["vehicle_km"] for r in routes), 2),
            "routes": len(routes), "served": len(served_ids),
            "unserved": len(requests) - len(served_ids),
            "total_wait_min": round(sum(value * weight for value, weight in waits), 2),
            "average_wait_min": round(sum(value * weight for value, weight in waits) / passenger_count, 2) if passenger_count else 0.0,
            "average_detour_km": round(sum(value * weight for value, weight in detours) / sum(weight for _, weight in detours), 2) if detours else 0.0,
            "occupancy_pct": round(seat_km / (len(routes) * capacity * sum(r["vehicle_km"] for r in routes)) * 100, 2)
            if routes and sum(r["vehicle_km"] for r in routes) else 0.0}
