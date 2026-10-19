import unittest

from routing import baseline, metrics, plan_routes


def request(rid, pickup="North Homes", minute=450, passengers=1, wait=10):
    return {"request_id": rid, "pickup": pickup, "destination": "Transit Station",
            "departure_min": minute, "passengers": passengers, "max_wait_min": wait}


class RoutingTests(unittest.TestCase):
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

    def test_oversized_request_explicitly_unserved(self):
        result = plan_routes([request("R1", passengers=7)], capacity=6)
        self.assertEqual(result["unserved"][0]["request"]["request_id"], "R1")


if __name__ == "__main__":
    unittest.main()
