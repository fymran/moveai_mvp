import pandas as pd
import streamlit as st

from routing import NODES, baseline, make_requests, metrics, plan_routes

st.set_page_config(page_title="MoveAI | Township Mobility", page_icon="🚌", layout="wide")
st.title("🚌 MoveAI")
st.subheader("Demand-responsive shared mobility for the last mile")
st.caption("Engineering Sprint 1 · Synthetic scenario only · Illustrative coordinates, not a real township or road network")

with st.sidebar:
    st.header("Simulation controls")
    n_requests = st.slider("Passenger requests", 8, 60, 24, 4)
    capacity = st.selectbox("Shuttle capacity (passengers)", [4, 6, 8, 12], index=1)
    window = st.slider("Departure compatibility window (minutes)", 3, 20, 8)
    wait_limit = st.slider("Maximum pickup wait (minutes)", 1, 20, 10)
    detour_limit = st.slider("Maximum passenger detour (synthetic km)", 0.0, 8.0, 2.5, 0.5)
    seed = st.number_input("Scenario seed", 1, 9999, 42, 1)
    st.caption("Changing the seed creates a different reproducible synthetic scenario.")

requests = make_requests(n_requests, int(seed))
for request in requests:
    request["max_wait_min"] = wait_limit
result = plan_routes(requests, capacity=capacity, time_window=window, max_detour_km=detour_limit)
routes, unserved = result["routes"], result["unserved"]
base = baseline(requests, capacity)
bm = metrics(requests, base["routes"], base["unserved"], capacity)
mm = metrics(requests, routes, unserved, capacity)

st.warning("All demand, coordinates, distance, and travel time below are synthetic model outputs. They are not measured service results, road distances, carbon savings, or a production dispatch plan.")
st.markdown("### Baseline versus MoveAI proposal")
comparison = pd.DataFrame([
    {"Metric": "Total vehicle distance (synthetic km)", "Individual-trip baseline": bm["vehicle_km"], "MoveAI heuristic": mm["vehicle_km"]},
    {"Metric": "Vehicles / routes", "Individual-trip baseline": bm["routes"], "MoveAI heuristic": mm["routes"]},
    {"Metric": "Requests served", "Individual-trip baseline": bm["served"], "MoveAI heuristic": mm["served"]},
    {"Metric": "Requests unserved", "Individual-trip baseline": bm["unserved"], "MoveAI heuristic": mm["unserved"]},
    {"Metric": "Total passenger waiting (synthetic min)", "Individual-trip baseline": bm["total_wait_min"], "MoveAI heuristic": mm["total_wait_min"]},
    {"Metric": "Average passenger detour (synthetic km)", "Individual-trip baseline": bm["average_detour_km"], "MoveAI heuristic": mm["average_detour_km"]},
    {"Metric": "Vehicle occupancy (seat-km / capacity seat-km)", "Individual-trip baseline": bm["occupancy_pct"], "MoveAI heuristic": mm["occupancy_pct"]},
])
st.dataframe(comparison, use_container_width=True, hide_index=True)

tab1, tab2, tab3 = st.tabs(["Overview", "Requests & routes", "Method and limitations"])
with tab1:
    st.markdown("### Illustrative synthetic network")
    map_data = pd.DataFrame([{"Place": k, "x": v[0], "y": v[1]} for k, v in NODES.items()])
    st.scatter_chart(map_data, x="x", y="y", color="Place", height=340)
    st.caption("Coordinates are illustrative points. No roads or geographic accuracy are represented.")
    st.markdown("### Proposed stop sequence")
    route_rows = [{"Vehicle": r["route_id"], "Requests": ", ".join(x["request_id"] for x in r["requests"]),
                   "Passengers / capacity": f"{r['passengers']} / {r['capacity']}",
                   "Stop order": " → ".join(r["stops"]), "Distance (synthetic km)": r["vehicle_km"],
                   "Waits (synthetic min)": ", ".join(f"{k}: {v:.1f}" for k, v in r["waits"].items()),
                   "Detours (synthetic km)": ", ".join(f"{k}: {v:.2f}" for k, v in r["detours"].items())}
                  for r in routes]
    st.dataframe(pd.DataFrame(route_rows), use_container_width=True, hide_index=True)

with tab2:
    req_df = pd.DataFrame(requests)
    if not req_df.empty:
        req_df["departure"] = req_df["departure_min"].map(lambda x: f"{x//60:02d}:{x%60:02d}")
        st.dataframe(req_df.drop(columns="departure_min").rename(columns={"departure": "Requested departure"}), use_container_width=True, hide_index=True)
    st.markdown("### Unserved or infeasible requests")
    if unserved:
        st.dataframe(pd.DataFrame([{"Request": x["request"]["request_id"], "Reason": x["reason"]} for x in unserved]), use_container_width=True, hide_index=True)
    else:
        st.success("Every request was assigned to exactly one feasible route in this scenario.")
    st.download_button("Download synthetic requests (CSV)", pd.DataFrame(requests).to_csv(index=False).encode("utf-8"), "moveai_synthetic_requests.csv", "text/csv")

with tab3:
    st.markdown("### Method")
    st.markdown("Requests are sorted by desired departure. A deterministic greedy heuristic starts with the earliest request and adds nearby, time-compatible requests only when the entire proposed route passes capacity, pickup-wait, and passenger-detour checks. Stops are ordered by requested departure; pickup events occur before the final common station drop-off. The comparison baseline assigns one vehicle per request. Both plans use the same synthetic Manhattan distance proxy.")
    st.markdown("### Metric definitions")
    st.markdown("- **Vehicle distance:** sum of synthetic distances along each vehicle's stop sequence; the model starts each vehicle at its first pickup and omits depot/repositioning travel.\n- **Waiting:** pickup arrival minus requested departure, with vehicles allowed to wait for a later request; waiting must stay within that request's limit.\n- **Passenger detour:** shared ride distance from pickup to station minus that passenger's direct synthetic distance.\n- **Occupancy:** passenger-kilometres divided by capacity seat-kilometres across routes.\n- **Baseline:** one direct vehicle trip per request, with the same distance model and capacity setting.")
    st.markdown("### Limitations")
    st.markdown("- The coordinate grid, Manhattan distance scale, and constant 24 km/h conversion are illustrative synthetic assumptions, not real geography, roads, or observed travel times.\n- Departure compatibility uses a maximum spread from the earliest request; the model has no live traffic, dwell time, boarding variability, vehicle depot, or station departure schedule.\n- Greedy assignment depends on request order and can miss better groupings. It does not claim global optimality.\n- This demo does not estimate adoption, emissions, costs, demand forecasts, or commercial outcomes.")

st.divider()
st.caption("MoveAI is an evaluation prototype. All displayed demand and network data are synthetic.")
