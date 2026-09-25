# ATLAS — Adaptive Track-Line Autonomous System

ATLAS races a known Corkscrew circuit from a standing start using standard SCR
commands. It learns a road-curvature map offline, plans speed and lateral
position over distance, and uses live sensors to follow that plan. It does not
change the car, physics, track, or submission livery.

**Sense → map → plan → control → measure → falsify → improve.**

## Current controller

`atlas_controller.py` extends the preserved spatial controller in
`experimental_controller.py`. The additional launch controller regulates clutch
using RPM and simulation time, only near the first standing start. Experimental
velocity-heading and steering-cap features default to disabled; they have not
earned promotion through measured gains.

The road map is sampled about every five meters. Its curvature comes from the
spatial derivative of road heading, reconstructed offline as vehicle yaw plus
SCR road-relative angle in an identified clean telemetry run. Runtime control
uses `distFromStart` to locate the car in this map. `build_track_model.py` and
the map's source-run metadata preserve its derivation.

Speed planning starts with a curvature limit, `v = sqrt(a_lateral / |curvature|)`,
capped by maximum speed. Local lateral-acceleration settings account empirically
for corner-specific behavior. A periodic backward pass applies braking
constraints, `v[i] <= sqrt(v[i+1]^2 + 2*a_brake*distance)`. These settings are
controller planning assumptions, not edits to the simulator's physical limits.
The active implementation has no forward acceleration pass; real engine,
traction and drag determine acceleration toward the envelope.

The line is a sequence of lateral-offset targets joined with cubic smoothstep
segments. Its derivative supplies a desired road-relative heading. Steering
combines curvature feedforward, speed-dependent compensation, heading and
lateral-position feedback, lateral-velocity damping, and a simulation-time rate
limit. Smoothstep gives continuous position and tangent at knots, but does not
guarantee continuous curvature. This is one remaining modeling limitation.

Throttle and brake follow the planned speed. Wheel-speed feedback reduces
throttle under excessive driven-wheel slip and reduces brake under apparent
locking. RPM thresholds and a simulated-time dwell govern gear changes.

## The response deadline

The installed SCR server waits about 10 ms for a command. A missed deadline can
hold the previous action and let a late UDP response become associated with a
later sensor state. Wall-time delay below the deadline does not advance physics
while the synchronous callback waits. See `TIMING.md` for measured
evidence and the distinction between observed GUI timing and overload probes.

Model loading, process startup, file creation and metadata collection happen
outside the active request/response exchange. The live client sends its command
before enqueueing a telemetry snapshot. A separate process writes CSV, full
packet evidence and the compact live display. A bounded, nonblocking queue
counts dropped records rather than allowing the disk to stop control.

## Evidence and promotion

Exploration uses accelerated headless runs. Each run preserves source snapshots,
parameters, copied race configuration, raw sensor/action packets, timing and
installed-asset hashes. The lap time is TORCS's `lastLapTime`, not a wall-clock
estimate. Spatial interpolation is used only to diagnose segment gains.

The unchanged local gate requires a complete standing-start lap, zero damage,
all 19 track sensors on road, continuous packet evidence, unchanged installed
assets and `|trackPos| <= 0.6` at every packet. It is a conservative engineering
gate, not an organizer-issued validity flag or an exact four-tire clearance test.

Fast experimental, repeated, timing-qualified and GUI-qualified results are
tracked separately. A new best is not automatically promoted. Qualification
repeats ordinary runs, fixed added response delay, and seeded replay of measured
GUI response jitter. A normal GUI run must use matching control sources,
parameters, map and assets and reproduce the qualified trajectory.

Historical references remain intact. Periodic reference laps stop a campaign
when its environment or protocol no longer reproduces known behavior. Failed
hypotheses and invalid laps remain evidence; they are not silently discarded to
make a benchmark look stronger.

## Boundaries

This curated package selects frozen RC1 and includes its exact runtime sources,
parameters, map, qualification report and representative traces. The raw laboratory
and Frontier experiments remain local. Use `competition_client.py` for ATLAS;
`torcs_jm_par.py` retains the historical reference default. Cloud CI runs compilation
and deterministic offline tests, not simulator qualification.
