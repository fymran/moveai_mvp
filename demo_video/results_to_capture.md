# Results to capture

Capture results from the running application, using the same synthetic request set and displayed settings for both approaches. Suggested reproducible starting settings are 24 requests, capacity 6, departure window 8 minutes, maximum wait 10 minutes, maximum detour 2.5 synthetic km, and seed 42. The app’s displayed run is authoritative; if settings differ, record the actual settings.

## Scenario record

| Field | Record from the run |
|---|---|
| Capture date and local time | ____________________ |
| App revision / Git commit (if available) | ____________________ |
| Request count | ____________________ |
| Capacity (passengers per vehicle) | ____________________ |
| Departure compatibility window (min) | ____________________ |
| Maximum pickup wait (min) | ____________________ |
| Maximum passenger detour (synthetic km) | ____________________ |
| Random seed | ____________________ |

## Values to transcribe from the comparison

| Metric | Individual-trip baseline | MoveAI heuristic |
|---|---:|---:|
| Total vehicle distance (synthetic km) | ______ | ______ |
| Routes / vehicles used | ______ | ______ |
| Requests served | ______ | ______ |
| Requests unserved | ______ | ______ |
| Total passenger waiting (synthetic passenger-minutes) | ______ | ______ |
| Average passenger waiting (synthetic min per served request) | ______ | ______ |
| Average passenger detour (synthetic km per served request) | ______ | ______ |
| Distance-weighted occupancy | ______ | ______ |

Copy the exact labels and displayed precision when possible. The average waiting and detour denominators are the served request count as implemented by the metrics function; do not reinterpret them as per-person averages. Occupancy is total passenger-kilometres divided by total capacity seat-kilometres for the routes. Confirm the dashboard’s accompanying definitions before narrating a metric.

## Route evidence

- Capture the request table with request IDs and generated pickup/departure details.
- Capture route IDs, assigned request IDs, pickup order, final Transit Station stop, passenger count/capacity, distance, waiting, and detour values.
- Capture the unserved request list, including any displayed reason. If no unserved requests are shown, record zero only when the app reports it.
- Ensure the route table and metric totals are from the same run and settings.

## Interpretation guardrails

- Distances and time estimates are synthetic model outputs, not measured driving distances or observed journey times.
- The baseline is one individual station trip per request; compare using the same demand and distance assumptions. Record any unserved demand on either side.
- Any displayed difference is specific to this synthetic scenario and heuristic. Do not call it verified savings, a forecast, an emissions reduction, or a guaranteed improvement.
- No published research statistic or local field study is cited by this prototype. Label local demand and service fit as hypotheses awaiting validation.
