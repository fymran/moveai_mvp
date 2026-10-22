# MoveAI demo video materials

This folder contains the production materials for a five-minute hackathon demonstration. It does not contain a rendered video. The application and all figures shown in the demo are a synthetic prototype; they are not measured results or evidence of a deployed service.

## Files

- `video_script.md` — timed narration and screen direction.
- `recording_checklist.md` — setup, capture, and evidence-integrity checklist.
- `results_to_capture.md` — scenario record and tables for transcribing actual on-screen output.
- `video_editing_plan.md` — edit, export, and hosting verification steps.

## Record the app

Follow the Windows setup and app launch commands in the repository root `README.md`. Use the default settings listed in the script for a reproducible walkthrough, then transcribe the exact values from the running dashboard. Do not invent or hand-edit outputs. The default seed reproduces synthetic demand under the current code; it does not make the assumptions representative of a real community.

The development checks run while preparing these materials were: `python -m unittest -v test_routing.py` (35 tests passed), `python -m unittest discover -v` (35 tests passed), Python AST parsing and imports of the app modules (passed; Streamlit 1.52.2 and pandas 2.3.3), and a Streamlit `AppTest` run with zero app exceptions. The headless AppTest also emitted bare-mode context and deprecated `use_container_width` warnings. These checks do not replace a manual browser recording check or prove that a rendered video exists.

No external published-study claim is used in the script. Local demand, resident fit, operator feasibility, and real-world outcomes remain hypotheses requiring evidence and stakeholder validation.
