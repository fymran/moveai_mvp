# MOVEAI_PROJECT_BRIEF.md

**Project:** Ubiquitous MoveAI  
**Competition:** Sime Darby Property University Hackathon 2026  
**Target submission deadline:** 23 October 2026 (confirm the official cutoff time and submission requirements)  
**Current working date when this brief was prepared:** 19 October 2026  
**Owner:** Solo builder  
**Primary assistant workflow:** ChatGPT Project for strategy/review; Codex in VS Code for editing and running the local codebase.

---

## 1. Project summary

MoveAI is a proposed demand-responsive shared-mobility coordination system for last-mile trips between residential areas and a public transport station.

The proposed web dashboard accepts ride requests, groups compatible trips, proposes shuttle routes, and compares the resulting plan against a defined baseline. The intended value is better shuttle utilization and less unnecessary vehicle travel without making passenger waiting time or detours unacceptable.

**Core pitch:** MoveAI helps township shuttle operators coordinate shared rides to transit by grouping compatible requests and planning routes under operational constraints.

## 2. Competition fit

- **Competition:** Sime Darby Property University Hackathon 2026.
- **Chosen theme:** Planet.
- **Chosen focus:** Green transport.
- **Initial use case:** Home-to-transit-station / last-mile commuting.
- **Prototype format:** Python web dashboard using Streamlit.
- **Intended prospective customer:** Township developer, township management organization, or shuttle operator.
- **Intended users:** Residents/passengers and transport operators.

The concept is intended to complement sustainable, transit-oriented township living. Do not claim Sime Darby Property has confirmed a specific operational need for MoveAI; this remains a hypothesis to validate.

## 3. Product scope

### MVP priorities

1. Generate or load passenger ride requests.
2. Group compatible requests into shared shuttle trips.
3. Assign requests to routes while respecting vehicle capacity.
4. Display proposed route assignments in a dashboard.
5. Compare MoveAI with a fair baseline using identical requests and consistent distance assumptions.
6. Report meaningful service and operating metrics.
7. Clearly label synthetic inputs, assumptions, and limitations.

### Out of scope for the initial MVP

- Production deployment or real dispatch operations.
- Real passenger accounts, payments, or booking confirmations.
- Autonomous driving.
- A generative-AI chatbot.
- Paid routing APIs unless specifically approved and feasible.
- Real GPS integration as a core dependency.
- Claims of verified emissions, cost, or service improvements without evidence.

## 4. Current implementation status

**Important:** This section reflects the project snapshot available when this brief was prepared. The local VS Code workspace may have changed since this snapshot. Update this section after reviewing the current files and running the tests.

The available snapshot contains:
- `app.py`
- `requirements.txt`
- `README.md`

The available `app.py` is a Streamlit dashboard that:
- Generates synthetic morning-commute requests.
- Uses illustrative township nodes and coordinates.
- Groups requests with a greedy heuristic based on pickup proximity, departure-time proximity, and capacity.
- Compares individual-trip and grouped-route distance proxies.
- Shows a scatter plot of illustrative locations and a route-assignment table.
- Explicitly warns that the results are simulated and do not establish real-world savings.

The available `README.md` says that:
- Coordinates are illustrative, not a real township map.
- Distance uses a grid-distance proxy rather than road-network distances.
- The grouping logic is a heuristic, not a globally optimal solver.
- Results do not establish real-world cost, service, or emissions savings.

### Known limitations in the available snapshot

- No separate `routing.py` module was present in the available snapshot.
- No `test_routing.py` was present in the available snapshot.
- The current route heuristic does not establish complete feasibility for actual pickup time windows, passenger waiting time, or passenger detours.
- The distance comparison is a simplified proxy and must not be presented as road-kilometre savings.
- Passenger occupancy and route metrics need precise definitions and tests.
- No real passenger, township, operator, or GPS data have been validated.

Do not assume these limitations still apply without inspecting the latest local files.

## 5. Technical direction

Preferred initial stack:
- Python
- Streamlit
- pandas
- Python standard library for basic logic and tests
- Optional Google OR-Tools only if installation and integration are justified by the remaining time

Suggested separation:
- `app.py`: Streamlit UI, controls, visualizations, result presentation.
- `routing.py`: request grouping, route planning, constraints, metric calculations.
- `test_routing.py`: deterministic automated tests.
- `README.md`: setup, methodology, metrics, limitations, and test instructions.

Keep the application Windows-friendly and avoid unnecessary dependencies.

## 6. Algorithm direction

The initial approach should be a transparent, deterministic vehicle-routing heuristic suitable for synthetic home-to-station trips. A greedy insertion heuristic is acceptable if the limitations are documented.

The implementation should, as far as the model supports:
- Respect vehicle capacity.
- Avoid duplicate request assignments.
- Account for every request, including unserved or infeasible requests.
- Ensure pickup events precede the corresponding drop-off.
- Enforce compatible departure/pickup windows.
- Enforce maximum passenger waiting time and detour limits where implemented.
- Use a consistent, documented travel-time/distance matrix.
- Avoid claims of global optimality.

Do not call this machine-learning demand prediction unless a real predictive model has been implemented and appropriately evaluated. The core MVP is an optimization/dispatch problem; generative AI is not required.

## 7. Baseline and validation

Use the same passenger requests, vehicle assumptions, and distance model for both MoveAI and the baseline. Do not deliberately weaken the baseline.

Potential metrics, only where validly calculated:
- Total vehicle distance (clearly label as synthetic distance proxy until road-network data are used).
- Number of routes/vehicles used.
- Requests served and unserved.
- Passenger waiting time.
- Passenger detour.
- Vehicle occupancy, with a stated formula.
- On-time arrival rate, if the simulation models arrival times.
- Estimated CO2e only if a documented, appropriate emissions factor and vehicle assumptions are used.

Testing should include:
- Single request.
- Compatible requests that can share a route.
- Capacity limits.
- Incompatible time windows.
- Waiting-time and detour limits.
- No duplicate assignments.
- Every request accounted for.
- Pickup-before-drop-off ordering.
- Deterministic results for identical inputs.
- Hand-verifiable metric calculations.

Synthetic results are simulation evidence only. They do not prove actual demand, user adoption, cost savings, or emissions reductions.

## 8. Business model hypothesis

Potential customer: township management, property developer, or shuttle operator.

Potential entry: a small paid or sponsored pilot after validating the operational need.

Potential longer-term pricing: subscription priced by township, fleet size, or service scale; integration/support could be priced separately.

Potential value:
- Better vehicle utilization.
- Lower unnecessary vehicle-kilometres.
- More predictable pickup service.
- Better visibility into demand and shuttle operations.

These are hypotheses, not validated commercial outcomes. A real business case needs operator interviews, cost assumptions, adoption estimates, and sensitivity analysis. Reduced kilometres do not automatically imply proportional savings in total operating cost because fixed costs may remain unchanged.

## 9. Solo project workflow

- **Project strategy chat (this conversation):** problem framing, prioritization, product decisions, business model, and challenge weak assumptions.
- **Development chat:** architecture, Codex prompts, code review, debugging, tests, and metric review.
- **Proposal/presentation chat:** proposal writing, slide narrative, pitch script, demo flow, and judge Q&A.
- **Codex in VS Code:** inspect and edit the actual local codebase, run tests, and report exact changes.

The project brief is the shared source of truth. Since separate chats may not automatically know the latest local code changes, provide updated files or a concise status report when needed.

## 10. Deadline plan

Target deadline: 23 October 2026.

1. Audit the current local code and preserve the working version.
2. Make routing logic testable and explicit.
3. Implement a fair baseline and correctly defined metrics.
4. Run reproducible tests across several demand scenarios.
5. Fix the most important correctness issues.
6. Capture honest screenshots/results and document assumptions.
7. Finalize proposal and pitch.
8. Confirm official submission format and cutoff time; keep a submission buffer.

## 11. Open questions

- What is the latest status of the local files after Codex changes?
- Have `routing.py` and `test_routing.py` been created and tested?
- What baseline is implemented, and is it operationally fair?
- Are pickup wait, detour, and capacity constraints actually enforced?
- Can a real township/operator problem be validated with credible evidence before submission?
- What are the official submission format and exact cutoff time?
- Is any road-network data available, or must the prototype remain clearly synthetic?

## 12. Rules for future changes

1. Inspect current files before editing.
2. Prefer small changes and tests over rewrites.
3. Never claim a test passed unless it was run.
4. Never invent user interviews, demand, commercial traction, or savings.
5. Label synthetic data and illustrative maps prominently.
6. Separate verified facts, assumptions, simulated results, and future plans.
7. Update this brief when important decisions or implementation status change.

## 13. Official hackathon briefing details transcribed from the user's slides

These details are taken from the hackathon briefing-slide images shared in this conversation. Follow any later official instructions if the organizers issue updates.

### Theme framing

- **Theme 1 — People:** “How might we enable every resident to live healthier, safer, more connected and more fulfilling lives?”
- **Theme 2 — Planet:** “How might we create townships that regenerate the environment and make sustainable living effortless?”
- Planet focus areas shown: Waste Management, Energy Efficiency, Green Transport, Climate Resilience, Circular Economy, Water Conservation, and Biodiversity.
- The briefing emphasizes solving one meaningful problem, validating it, and measuring environmental improvement.
- The process shown is: Observe → Identify → Understand → Create → Build.
- The six qualities of a strong solution are: Relevant, Impactful, Innovative, Feasible, Scalable, and Evidence Based.

### Submission requirements shown in the briefing

**Deadline: 11:59 PM, 23 October 2026.**

Required:
1. **Pitch deck:** maximum 10 main slides; appendix allowed.
2. **Video/demo link:** mandatory, with a 5-minute video or live demo link demonstrating the solution.
3. **Prototype/code link:** mandatory; link to the prototype, codebase, or GitHub repository.

Optional:
4. Supporting documents or additional links where applicable.

The briefing says incomplete submissions will not be considered. Confirm link access and submission-portal requirements before submitting.

### Judging criteria shown in the briefing

| Criterion | Weight | What it asks |
|---|---:|---|
| Impact & Sustainability Value | 25% | Meaningful and measurable resident, community, or environmental outcomes |
| Innovation & Differentiation | 20% | Genuine originality or a differentiated approach, not simply repackaging an existing solution |
| Feasibility & Deliverability | 20% | Whether the solution can realistically be piloted and implemented within a township |
| Strategic Fit & Theme Relevance | 15% | Clear connection to a People or Planet challenge and an SDP township priority |
| Commercial & Value Multiplication | 10% | Potential to create value for SDP, township businesses and/or residents, and scale |
| Team, Evidence & Pitch Quality | 10% | Research and validation, a credible solution, and clear communication |

### Implications for MoveAI

- Submission needs a deck, a working prototype/code link, and a 5-minute demo/video link. A written proposal alone is insufficient.
- Keep the main deck within 10 slides; move detailed methodology and test cases to an appendix if useful.
- Present the solo-builder status honestly and keep the scope realistic.
- Report simulation outcomes as simulation outcomes, not real-world impact. State the baseline and assumptions.
- For Innovation, compare MoveAI with fixed-route shuttles, simple dispatch, and ordinary booking/navigation tools; do not claim uniqueness without evidence.
- For Feasibility, show the running dashboard, actual test results, known limitations, and a practical pilot path.
- For Commercial Value, identify township operators or management as prospective customers, and label pricing/savings as hypotheses until validated.
- For Evidence, prioritize reproducible tests and real problem validation if feasible; do not invent interviews or demand.
- The 5-minute demo should show one end-to-end scenario: passenger requests → route assignment → baseline comparison → metrics and limitations.

### Submission checklist

- [ ] Main pitch deck has no more than 10 slides.
- [ ] Appendix is separate from the main deck.
- [ ] A 5-minute demo/video link is ready and accessible.
- [ ] Prototype/code link is ready and accessible to judges.
- [ ] Demo uses the same scenario and assumptions as the reported metrics.
- [ ] Simulated data and unvalidated claims are labelled.
- [ ] All required deliverables are submitted before 11:59 PM on 23 October 2026.
