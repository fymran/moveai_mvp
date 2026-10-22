# Recording checklist

## Environment and app

- [ ] Use a clean desktop with notifications and unrelated windows closed.
- [ ] From the project directory, activate the project virtual environment and run `streamlit run app.py` (see the root README for setup).
- [ ] Open the local Streamlit URL in a desktop browser and confirm the dashboard renders.
- [ ] Use the agreed demo settings: 24 requests, capacity 6, window 8 min, wait limit 10 min, detour limit 2.5 synthetic km, seed 42.
- [ ] Confirm the synthetic-data warning, comparison, route details, and limitations section are visible and readable.
- [ ] Record the values actually displayed; do not assume results from an earlier run.
- [ ] Check that no route has an occupancy above capacity and that served plus unserved requests account for the full generated set.

## Capture

- [ ] Record at 1920×1080 or the highest stable display resolution, 30 fps, with browser zoom chosen so labels remain legible.
- [ ] Capture the browser/app window only; hide address-bar details if they reveal personal information, but do not hide the app’s synthetic-data disclosures.
- [ ] Record microphone narration in a quiet room; do a short level check and listen back for clipping or background noise.
- [ ] Follow `video_script.md` scene timings. Scroll deliberately and pause on tables long enough to read them.
- [ ] If a widget is changed, state that this is a new synthetic scenario and show the changed setting.
- [ ] Capture a clean final screen with project name and synthetic-data disclaimer.
- [ ] Save the unedited source recording to a private working folder; do not put large video files in the source repository unless required.

## Evidence and integrity

- [ ] Keep an evidence note of app version/commit, date, settings, seed, and values visible in the recorded run.
- [ ] Do not add or imply real township locations, passenger interviews, customer adoption, verified research outcomes, emissions savings, or commercial results.
- [ ] Do not replace actual app output with composited or selectively edited numbers.
- [ ] If a runtime error or inconsistent metric appears, stop capture and investigate before recording the final take.
