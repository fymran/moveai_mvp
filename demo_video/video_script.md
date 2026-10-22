# Ubiquitous MoveAI — 5-minute demo video script

**Target runtime:** about 4:45 (acceptable range: 4:30–5:00)  
**Format:** screen recording of the running Streamlit prototype with voice-over and captions.  
**Data status:** every request, coordinate, distance, route, and metric shown by this MVP is synthetic. Read the values from the live run; do not substitute estimates or imply measured local outcomes.

## Before recording

Run the app using the steps in `README.md`. Use the default controls for a reproducible walkthrough: 24 requests, capacity 6, departure window 8 minutes, maximum pickup wait 10 minutes, maximum passenger detour 2.5 synthetic km, and seed 42. The app recalculates when its controls change. Confirm the visible settings and values before recording. If a value differs, narrate the value actually on screen.

Do not edit the source or manually alter the output for the recording. If you change a control during the demo, identify the change and treat the new result as a different synthetic scenario.

## Timed script and screen direction

### 0:00–0:25 — Opening

**Screen:** dashboard title, then the synthetic-data notice. Keep the app visible.

**Narration:** “This is Ubiquitous MoveAI, a prototype for grouping synthetic home-to-transit shuttle requests. It demonstrates how a dispatcher could compare individual trips with a simple shared-route heuristic. The data and results in this demo are simulated; they are not measurements from a real township or shuttle service.”

### 0:25–0:55 — Problem hypothesis and intended value

**Screen:** overview and the demand/request summary. Do not add stock footage implying real riders or a real service.

**Narration:** “The problem we want to explore is coordinating nearby trips to a common transit station. This prototype is a way to inspect that idea. We have not validated local demand, rider preferences, operating costs, or service quality with residents or operators. No published-study statistic is being used here to claim that this particular service will work.”

### 0:55–1:35 — Inputs and reproducibility

**Screen:** show request count, vehicle capacity, departure compatibility window, maximum pickup wait, maximum passenger detour, and random seed. Point to the synthetic-data and methodology notes.

**Narration:** “These controls define one simulated scenario. We have 24 generated requests, a six-passenger vehicle capacity, an eight-minute departure window, a ten-minute maximum pickup wait, and a 2.5-kilometre synthetic detour limit. Seed 42 makes the generated scenario repeatable. Locations and distances are illustrative, not real road-network data. Changing a control reruns the scenario.”

### 1:35–2:30 — Proposed route assignments

**Screen:** open the requests and routes view. Show request IDs, route assignments, route stop order, passenger load versus capacity, wait, and detour fields. Scroll slowly; keep labels legible.

**Narration:** “The planner orders requests by desired departure and builds routes with a deterministic greedy heuristic. It considers nearby pickups, capacity, departure compatibility, each request’s maximum wait, and the passenger detour limit. Pickups precede the shared transit-station drop-off. The displayed route list is the planner’s actual output for this seed, including any unserved requests. This is an explainable heuristic, not a globally optimal solution.”

### 2:30–3:35 — Fair baseline comparison

**Screen:** show the baseline-versus-MoveAI comparison table and metric definitions. Keep the same scenario settings in view if possible.

**Narration:** “The baseline gives each request an individual trip to the same transit station, using the same generated requests and synthetic distance model. Requests that exceed vehicle capacity are reported as unserved there too. The table reports total vehicle-kilometres, routes, served and unserved requests, passenger waiting, passenger detour, and distance-weighted occupancy. These are outputs of this simulation, not observed service results. Any difference is conditional on these assumptions and this heuristic.”

### 3:35–4:15 — Constraints and limitations

**Screen:** show the unserved requests or route detail, then the methodology and limitations section.

**Narration:** “A request can remain unserved when constraints prevent assignment. The model uses a synthetic Manhattan-style distance proxy and a fixed assumed speed for wait estimates. It does not model real roads, traffic, depots, repositioning, boarding time, transit timetables, or measured passenger behavior. It does not calculate validated emissions or cost savings. Those gaps matter before any operational claim.”

### 4:15–4:45 — Next step and close

**Screen:** return to the overview with the scenario controls and synthetic-data notice visible. End on the project name.

**Narration:** “The next step is to validate the assumptions with local residents and transport operators, then replace illustrative inputs with appropriately collected and verified data. MoveAI is currently a reproducible routing demonstration—not a deployed shuttle service or a forecast. Thank you.”

## Caption and edit notes

- Burn in accurate captions for all narration; proofread names, units, and “passenger-minutes.”
- Keep the notice **“Synthetic simulation — illustrative inputs, not measured results”** visible during metric comparisons.
- Do not add music, imagery, maps, logos, or testimonials that imply real deployment, endorsement, or research evidence without permission and evidence.
- If narration uses a numeric output, read it directly from the captured run and retain enough screen time for viewers to inspect it. Do not describe it as a real-world saving.
