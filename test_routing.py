import unittest
from copy import deepcopy

from routing import baseline, metrics, plan_routes


def request(rid, pickup="North Homes", minute=450, passengers=1, wait=10,
            destination="Transit Station"):
    return {"request_id": rid, "pickup": pickup, "destination": destination,
            "departure_min": minute, "passengers": passengers, "max_wait_min": wait}


class RoutingTests(unittest.TestCase):
    def test_public_boundaries_reject_missing_fields_and_unknown_nodes(self):
        valid = request("R1")
        missing = {key: value for key, value in valid.items() if key != "destination"}
        unknown = {**valid, "pickup": "Unknown Homes"}
        for invalid, message in ((missing, "missing required fields"),
                                 (unknown, "unknown pickup node")):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, message):
                plan_routes([invalid])
            with self.subTest(boundary="baseline", invalid=invalid), self.assertRaisesRegex(ValueError, message):
                baseline([invalid])
            with self.subTest(boundary="metrics", invalid=invalid), self.assertRaisesRegex(ValueError, message):
                metrics([invalid], [], [], 4)

    def test_destination_must_be_transit_station(self):
        valid = request("R1", destination="Transit Station")
        self.assertEqual(len(plan_routes([valid])["routes"]), 1)
        for destination, message in (("North Homes", "destination must be 'Transit Station'"),
                                     ("Unknown Place", "unknown destination node")):
            invalid = request("R1", destination=destination)
            with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, message):
                plan_routes([invalid])

    def test_invalid_capacity_and_numeric_constraints_are_rejected(self):
        reqs = [request("R1")]
        invalid_capacities = (-1, 0, 2.5, True, float("nan"), float("inf"), "4")
        for capacity in invalid_capacities:
            for operation in (lambda: plan_routes(reqs, capacity=capacity),
                              lambda: baseline(reqs, capacity=capacity),
                              lambda: metrics(reqs, [], [], capacity)):
                with self.subTest(capacity=capacity), self.assertRaisesRegex(ValueError, "capacity must be a positive integer"):
                    operation()
        for time_window in (-1, True, float("nan"), float("inf"), "1"):
            with self.subTest(time_window=time_window), self.assertRaisesRegex(ValueError, "time_window"):
                plan_routes(reqs, time_window=time_window)
        for detour in (-1, True, float("nan"), float("inf"), "1"):
            with self.subTest(detour=detour), self.assertRaisesRegex(ValueError, "max_detour_km"):
                plan_routes(reqs, max_detour_km=detour)

        # Integer-valued numeric capacities and fractional non-negative windows remain supported.
        self.assertEqual(len(plan_routes(reqs, capacity=4.0, time_window=1.5,
                                         max_detour_km=0.5)["routes"]), 1)

    def test_fractional_departure_windows_are_compared_without_truncation(self):
        within = [request("R1", minute=450.1), request("R2", minute=451.4)]
        outside = [request("R1", minute=450.1), request("R2", minute=451.7)]
        self.assertEqual(len(plan_routes(within, 4, 1.5, 1.0)["routes"]), 1)
        self.assertEqual(len(plan_routes(outside, 4, 1.5, 1.0)["routes"]), 2)

    def test_integer_departure_window_behavior_is_unchanged(self):
        within = [request("R1", minute=450), request("R2", minute=451)]
        outside = [request("R1", minute=450), request("R2", minute=452)]
        self.assertEqual(len(plan_routes(within, 4, 1, 1.0)["routes"]), 1)
        self.assertEqual(len(plan_routes(outside, 4, 1, 1.0)["routes"]), 2)

    def test_public_boundaries_reject_invalid_passenger_counts(self):
        for passengers in (0, -1, 1.5, True):
            invalid = request("R1", passengers=passengers)
            for operation in (lambda: plan_routes([invalid]), lambda: baseline([invalid]),
                              lambda: metrics([invalid], [], [], 4)):
                with self.subTest(passengers=passengers), self.assertRaisesRegex(ValueError, "positive integer"):
                    operation()

    def test_integral_numeric_passenger_count_remains_supported(self):
        result = plan_routes([request("R1", passengers=2.0)])
        self.assertEqual(result["routes"][0]["passengers"], 2)

    def test_public_boundaries_reject_duplicate_ids(self):
        duplicate_requests = [request("R1"), request("R1", pickup="West Homes")]
        for operation in (lambda: plan_routes(duplicate_requests),
                          lambda: baseline(duplicate_requests),
                          lambda: metrics(duplicate_requests, [], [], 4)):
            with self.assertRaisesRegex(ValueError, "duplicate request_id"):
                operation()

    def test_public_boundaries_reject_negative_wait_limits(self):
        invalid = request("R1", wait=-0.1)
        for operation in (lambda: plan_routes([invalid]), lambda: baseline([invalid]),
                          lambda: metrics([invalid], [], [], 4)):
            with self.assertRaisesRegex(ValueError, "max_wait_min must be non-negative"):
                operation()

    def test_public_boundaries_reject_invalid_departure_values(self):
        for departure in ("450", float("nan"), float("inf"), True):
            invalid = {**request("R1"), "departure_min": departure}
            with self.subTest(departure=departure), self.assertRaisesRegex(ValueError, "departure_min"):
                plan_routes([invalid])

    def test_single_request(self):
        result = plan_routes([request("R1")])
        self.assertEqual(len(result["routes"]), 1)
        self.assertEqual(result["routes"][0]["requests"][0]["request_id"], "R1")

    def test_compatible_requests_share(self):
        result = plan_routes([request("R1", "North Homes", 450), request("R2", "North Homes", 452)], 4, 8, 3)
        self.assertEqual(len(result["routes"]), 1)
        self.assertEqual(result["routes"][0]["passengers"], 2)

    def test_capacity_excess_splits(self):
        result = plan_routes([request("R1", passengers=2), request("R2", passengers=2)], 3)
        self.assertEqual(len(result["routes"]), 2)
        self.assertTrue(all(r["passengers"] <= 3 for r in result["routes"]))

    def test_outside_departure_window_does_not_group(self):
        result = plan_routes([request("R1", minute=450), request("R2", minute=470)], 4, 8)
        self.assertEqual(len(result["routes"]), 2)

    def test_wait_constraint_prevents_grouping(self):
        result = plan_routes([request("R1", "North Homes", 450, wait=0),
                              request("R2", "West Homes", 450, wait=0)], 4, 8, 10)
        self.assertEqual(len(result["routes"]), 2)

    def test_detour_constraint_prevents_grouping(self):
        result = plan_routes([request("R1", "North Homes"), request("R2", "South Homes")], 4, 8, 0)
        self.assertEqual(len(result["routes"]), 2)

    def test_no_duplicate_assignments(self):
        reqs = [request(f"R{i}", "North Homes", 450+i) for i in range(5)]
        result = plan_routes(reqs, 3, 8)
        assigned = [r["request_id"] for route in result["routes"] for r in route["requests"]]
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_every_request_accounted_for(self):
        reqs = [request("R1"), request("R2", passengers=9), request("R3", minute=500)]
        result = plan_routes(reqs, 6)
        assigned = {r["request_id"] for route in result["routes"] for r in route["requests"]}
        missing = {x["request"]["request_id"] for x in result["unserved"]}
        self.assertEqual(assigned | missing, {r["request_id"] for r in reqs})
        self.assertFalse(assigned & missing)

    def test_pickups_precede_station_dropoff(self):
        route = plan_routes([request("R1"), request("R2", minute=452)], 4, 8)["routes"][0]
        self.assertEqual(route["stops"][-1], "Transit Station")
        self.assertEqual(len(route["pickup_times"]), 2)
        self.assertLessEqual(route["pickup_times"][0], route["pickup_times"][1])

    def test_deterministic(self):
        reqs = [request("R2", "West Homes", 452), request("R1", "North Homes", 450)]
        self.assertEqual(plan_routes(reqs), plan_routes(reqs))

    def test_hand_verifiable_metrics(self):
        reqs = [request("R1", "North Homes", passengers=2)]
        baseline_result = baseline(reqs, 4)
        summary = metrics(reqs, baseline_result["routes"], baseline_result["unserved"], 4)
        self.assertEqual(summary["vehicle_km"], 3.36)
        self.assertEqual(summary["routes"], 1)
        self.assertEqual(summary["served"], 1)
        self.assertEqual(summary["unserved"], 0)
        self.assertEqual(summary["occupancy_pct"], 50.0)

    def test_occupancy_uses_each_routes_capacity_and_distance(self):
        reqs = [request("R1", passengers=2), request("R2", passengers=1)]
        routes = [
            {"requests": [reqs[0]], "passengers": 2, "capacity": 4,
             "vehicle_km": 10.0, "waits": {"R1": 0.0}, "detours": {"R1": 0.0}},
            {"requests": [reqs[1]], "passengers": 1, "capacity": 2,
             "vehicle_km": 20.0, "waits": {"R2": 0.0}, "detours": {"R2": 0.0}},
        ]
        summary = metrics(reqs, routes, [], capacity=99)
        # (2*10 + 1*20) passenger-km / (4*10 + 2*20) seat-km = 50%.
        self.assertEqual(summary["occupancy_pct"], 50.0)

    def test_passenger_weighted_wait_metrics(self):
        reqs = [request("R1", passengers=2), request("R2", passengers=1)]
        routes = [{"requests": reqs, "passengers": 3, "capacity": 4,
                   "vehicle_km": 10.0, "waits": {"R1": 2.0, "R2": 4.0},
                   "detours": {"R1": 0.0, "R2": 0.0}}]
        summary = metrics(reqs, routes, [], capacity=4)
        self.assertEqual(summary["total_wait_min"], 8.0)
        self.assertEqual(summary["average_wait_min"], 2.67)

    def test_exact_wait_and_detour_values_at_constraint_boundaries(self):
        reqs = [request("R1", "North Homes", 450),
                request("R2", "Central Residences", 450)]
        reqs[1]["max_wait_min"] = 6.3
        accepted = plan_routes(reqs, capacity=4, time_window=8, max_detour_km=1.2)
        self.assertEqual(len(accepted["routes"]), 1)
        route = accepted["routes"][0]
        self.assertAlmostEqual(route["waits"]["R2"], 6.3)
        self.assertEqual(route["detours"]["R1"], 1.2)
        self.assertEqual(route["detours"]["R2"], 0.0)

        rejected_wait = [dict(r) for r in reqs]
        rejected_wait[1]["max_wait_min"] = 6.29
        self.assertEqual(len(plan_routes(rejected_wait, 4, 8, 1.2)["routes"]), 2)
        self.assertEqual(len(plan_routes(reqs, 4, 8, 1.19)["routes"]), 2)

    def test_candidate_that_breaks_full_trial_route_is_rejected(self):
        reqs = [request("R1", "North Homes", 450, wait=30),
                request("R2", "Central Residences", 450, wait=30),
                request("R3", "Lake Residences", 450, wait=30)]
        result = plan_routes(reqs, capacity=4, time_window=8, max_detour_km=4.0)
        route_members = [{r["request_id"] for r in route["requests"]} for route in result["routes"]]
        self.assertIn({"R1", "R3"}, route_members)  # feasible pair, 3.84 km detour for R1
        self.assertIn({"R2"}, route_members)  # adding R2 makes the full stop sequence exceed the limit

    def test_metrics_reject_duplicate_and_inconsistent_assignments(self):
        reqs = [request("R1"), request("R2", pickup="West Homes")]
        base = baseline(reqs, capacity=4)
        with self.assertRaisesRegex(ValueError, "duplicate request assignments"):
            metrics(reqs, base["routes"] + [base["routes"][0]], [], 4)
        with self.assertRaisesRegex(ValueError, "duplicate request assignments"):
            metrics(reqs, base["routes"], [{"request": reqs[0], "reason": "test"}], 4)
        with self.assertRaisesRegex(ValueError, "missing from routes and unserved"):
            metrics(reqs, base["routes"][:1], [], 4)

    def test_metrics_reject_unknown_route_or_unserved_ids(self):
        reqs = [request("R1")]
        route = {"requests": [request("OTHER")], "passengers": 1, "capacity": 4,
                 "vehicle_km": 1.0, "waits": {}, "detours": {}}
        with self.assertRaisesRegex(ValueError, "unknown request IDs"):
            metrics(reqs, [route], [], 4)
        with self.assertRaisesRegex(ValueError, "unknown request IDs"):
            metrics(reqs, [], [{"request": request("OTHER"), "reason": "test"}], 4)

    def test_metrics_rejects_malformed_route_metric_data(self):
        reqs = [request("R1", passengers=2)]
        valid = baseline(reqs, capacity=4)["routes"][0]

        invalid_routes = []
        for value in (-1.0, float("nan"), float("inf"), True, "3.0"):
            route = deepcopy(valid)
            route["vehicle_km"] = value
            invalid_routes.append((route, "vehicle_km"))
        for value in (0, 1, 2.5, True):
            route = deepcopy(valid)
            route["passengers"] = value
            invalid_routes.append((route, "passengers"))
        for value in (0, -1, 2.5, True, float("nan")):
            route = deepcopy(valid)
            route["capacity"] = value
            invalid_routes.append((route, "capacity"))
        for field, value in (("waits", -1.0), ("waits", float("nan")),
                             ("waits", True), ("detours", -1.0),
                             ("detours", float("inf")), ("detours", True)):
            route = deepcopy(valid)
            route[field]["R1"] = value
            invalid_routes.append((route, field))

        for route, message in invalid_routes:
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, message):
                metrics(reqs, [route], [], 4)

        route = deepcopy(valid)
        route["waits"]["OTHER"] = 0.0
        with self.assertRaisesRegex(ValueError, "waits entries must reference assigned"):
            metrics(reqs, [route], [], 4)
        route = deepcopy(valid)
        del route["detours"]["R1"]
        with self.assertRaisesRegex(ValueError, "detours must include every assigned"):
            metrics(reqs, [route], [], 4)
        route = deepcopy(valid)
        route.pop("vehicle_km")
        with self.assertRaisesRegex(ValueError, "requires vehicle_km and passengers"):
            metrics(reqs, [route], [], 4)

    def test_zero_distance_occupancy_returns_zero(self):
        reqs = [request("R1", pickup="Transit Station", passengers=2)]
        baseline_result = baseline(reqs, capacity=4)
        summary = metrics(reqs, baseline_result["routes"], baseline_result["unserved"], 4)
        self.assertEqual(summary["vehicle_km"], 0.0)
        self.assertEqual(summary["occupancy_pct"], 0.0)

    def test_multi_request_baseline_metrics(self):
        reqs = [request("R1", "North Homes", passengers=2),
                request("R2", "South Homes"),
                request("R3", "East Homes"),
                request("R4", "Lake Residences", passengers=5)]
        baseline_result = baseline(reqs, capacity=4)
        summary = metrics(reqs, baseline_result["routes"], baseline_result["unserved"], 4)
        self.assertEqual(summary["vehicle_km"], 10.32)
        self.assertEqual(summary["routes"], 3)
        self.assertEqual(summary["served"], 3)
        self.assertEqual(summary["unserved"], 1)
        # (2*3.36 + 3.12 + 3.84) / (4*(3.36 + 3.12 + 3.84)) * 100.
        self.assertEqual(summary["occupancy_pct"], 33.14)

    def test_oversized_request_explicitly_unserved(self):
        result = plan_routes([request("R1", passengers=7)], capacity=6)
        self.assertEqual(result["unserved"][0]["request"]["request_id"], "R1")


if __name__ == "__main__":
    unittest.main()
