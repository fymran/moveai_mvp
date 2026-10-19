# Ubiquitous MoveAI — MVP

A Streamlit prototype for coordinating synthetic home-to-transit-station shuttle requests. It demonstrates a transparent grouping heuristic and compares it with one direct vehicle trip per request. This is a software demo, not measured transport analysis.

## Windows setup and run

Use Python 3.10 or newer in PowerShell from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run the venv executable directly: `.\.venv\Scripts\python.exe -m streamlit run app.py`.

## Run tests

```powershell
python -m unittest -v test_routing.py
```

The tests use Python's built-in `unittest`; no additional test dependency is needed.

## Routing algorithm

`routing.py` contains synthetic request generation, distance and travel-time assumptions, the individual-trip baseline, route grouping, feasibility checks, and metrics. Requests are processed in deterministic departure order. Starting from the earliest outstanding request, the heuristic tries other requests by pickup proximity and adds them only if the whole proposed route respects vehicle passenger capacity, the maximum departure-time spread, every passenger's maximum pickup wait, and every passenger's maximum detour. Pickup stops are ordered by requested departure, followed by the common transit-station drop-off. A request larger than vehicle capacity is explicitly unserved; other requests are assigned to a feasible route, usually alone when they cannot be grouped.

This greedy heuristic is explainable and reproducible but order-dependent. It does not guarantee a globally optimal grouping or minimum-distance solution.

## Metric definitions

- **Vehicle kilometres:** sum of route leg distances. Each vehicle starts at its first pickup; depot and repositioning mileage is omitted.
- **Routes / vehicles:** one vehicle per planned route. The baseline deliberately uses one direct vehicle per request.
- **Served / unserved requests:** counts by request ID. A request is served if included in a route; over-capacity requests are unserved.
- **Passenger waiting:** pickup arrival time minus requested departure time, weighted by the number of passengers on each request, then summed and averaged per passenger. The model allows a vehicle to wait until a later request's requested time.
- **Passenger detour:** distance ridden from a passenger's pickup to the station minus that passenger's direct synthetic distance.
- **Vehicle occupancy:** passenger-kilometres / capacity seat-kilometres, weighted by vehicle route distance. This describes passenger seat utilization in this simplified model, not time-based occupancy.

## Synthetic-data assumptions

All trip demand and coordinates are generated for the demo. Named residential areas and plotted coordinates are illustrative only, not real township locations. Distance is a Manhattan grid distance across illustrative coordinates, multiplied by 1.2 synthetic kilometres per coordinate unit. Travel time uses a constant synthetic speed of 24 km/h. Neither is road-network or observed data. Baseline and grouped routes use this same distance model and the same requests.

## Limitations and next improvements

The model has one station destination and no vehicle depots, repositioning, traffic, service dwell, boarding variation, transit schedule, or dynamic dispatch. Requested departure is treated as the earliest acceptable pickup time, with an explicit maximum wait. The route heuristic uses greedy candidate selection and does not search all possible partitions or stop permutations. Results do not establish real demand, adoption, cost, service quality, emissions, or commercial impact. Do not interpret distance differences as verified carbon savings.

The most valuable next step is to replace the synthetic distance and speed assumptions with a reviewed, consistently applied travel-time matrix for a defined study area, then validate route feasibility with local transport stakeholders before presenting operational claims.
