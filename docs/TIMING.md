> Historical investigation record. Paths under `audit/` and unlisted experiment IDs
> refer to the retained local laboratory, not missing release dependencies.
> The packaged final evidence is `../evidence/qualification.json` and the selected
> traces listed in `../evidence/fixture_inventory.json`.

# Measured SCR timing mechanism

2026-09-24. Installed simulator, physics, car and livery are unchanged.

## Cause and quantitative model

The controller does not acquire a different simulation timestep merely because
it takes 2 ms to respond. The race engine invokes SCR synchronously, before
physics integration. Physics integration is 0.002 s; the driver callback tests
a 0.020 s interval. Floating-point accumulation yields 10 or 11 integration
steps (20 or 22 ms) between observed sensor samples. The countdown transition
has one observed 40 ms interval, equally present in GUI and headless traces.

SCR sends sensors, waits with `select` for up to **10000 microseconds**, receives
one datagram, parses it and applies its action. While this callback waits,
physics does not advance. A response received before the deadline adds **zero
integration steps**. On timeout, binary branch 0x7b8c -> 0x7611 copies oldAccel,
oldBrake, oldGear, oldSteer and oldClutch back to the car and returns. Physics
then advances to the next callback: another **10/11 steps with the old action**.
SCR provides no request/action sequence number and does not discard stale
commands. A late command can therefore be consumed after a newer sensor packet.

Evidence:

- `audit/raceengine_disassembly.txt`: ReOneStep invokes the robot callback before
  the simulation update; callback threshold at rodata 0xfd48 is 0.020 s.
- `audit/timing_scr_server_disassembly.txt`: select at 0x796a; receive at 0x7996;
  timeout branch and old-action restoration as above.
- `timing_observer.c`: observation-only select/send/receive forwarding, compiled
  locally; enabled only with `--observe-server`. No qualification result requires
  the observer. Installed binaries are never patched.
- `experiments/20260924T191051_150229Z_experimental-v3`: inline logging took
  **9.547 ms after packet 1's send**. The next roughly 2.3 ms response then
  missed the packet-2 deadline. Its select elapsed 10.126 ms and returned zero.
  A second timeout is after the last client response during shutdown and must
  not be counted as an in-race failure.
- `20260924T191053_095461Z_experimental-v3`: same 2 ms delay, buffered logging,
  no select timeout in the 150-packet probe.
- `20260924T191055_143690Z_experimental-v3`: a deliberate single 15 ms
  post-send stall causes exactly one packet-2 timeout.
- `20260924T192806_495804Z_experimental-v3`: receive-level tracing confirms
  that packet 2's `steer -0.120` reply is consumed at **server packet 3**, at
  simulation time -0.942 instead of -0.962. Packet 3's reply then arrives at
  packet 4. This directly demonstrates the stale-command phase shift.
- `20260924T190951_761345Z_experimental-v3`: deliberate 12 ms responses produce
  298 sensor/select events for 150 client responses, with 148 timeouts. This
  demonstrates queue backlog, not a larger physics timestep.

Thus response timing must include **time from server send to client receive**,
including unfinished post-send work from the previous iteration. Measuring only
the Python compute/sleep interval understated the deadline risk. The original
Windows-mounted filesystem flush was in that critical path.

## Measured competition GUI timing

The normal GUI was launched with project-local copies of the race configuration,
through Race -> Practice -> New Race on the existing noVNC desktop. Same installed
car/driver/track/physics; no headless command-line race flag. Run:
`experiments/20260924T190741_134214Z_experimental-v3`.

| Metric, ms | Mean | Median | p95 | p99 | Maximum | Stddev |
|---|---:|---:|---:|---:|---:|---:|
| GUI client receive -> send | .295 | .265 | .451 | .596 | 2.521 | .092 |
| GUI response send interval | 21.011 | 20.366 | 28.313 | 31.133 | 76.215 | 4.522 |
| Buffered headless receive -> send | .092 | .075 | .172 | .363 | .829 | .052 |

Headless comparison: `20260924T190709_178614Z_experimental-v3`; complete interval
distributions, including wall and simulation intervals, are in each run's
`timing_analysis.json`. Rendering introduces wall-clock packet-spacing jitter;
that is different from response latency after a packet has been sent. Injecting
21 ms of response delay would not reproduce this GUI workload.

The GUI completed **89.394 s**, identical full sensor/action hash to the seven
historical headless confirmations. Observed peak 218.010 km/h, max |trackPos|
0.593865, zero damage. No official organizer certification is implied.

## Correction and qualification envelope

`timing_experiment.py --buffer-logging` retains full records in memory and writes
them after the simulator exits, including Python exception/Ctrl+C cleanup.
`async_telemetry.py` moves submission CSV/raw logging and 5 Hz live status into
a separate process with a bounded queue; startup completes before the handshake.
Queue saturation drops telemetry with an explicit count rather than blocking
control. `competition_client.py` preloads model/parameters before handshake and
uses this output process. It attaches to normal GUI SCR and never launches or
modifies TORCS. `torcs_jm_par.py` remains the preserved reference entry point.

The initial suite (`audit/timing_qualification.json`) tests both controllers
under the same three timing conditions:

1. Ordinary buffered accelerated headless.
2. Fixed 3 ms injected response delay, above the measured GUI maximum;
   measured total response maxima 4.087–5.294 ms in the candidate repetitions.
3. Seeded resampling of the actual GUI receive-to-send distribution, added to
   normal compute/transport time, a conservative replay of measured jitter.

Candidate: **9/9**, all 89.394 with the original trace hash. Reference: **6/6**,
all 95.310 with its original trace hash. The separate 2 ms buffered full lap also
matches exactly. The artificial 12 ms overload diagnoses the deadline mechanism;
it is outside the observed GUI response envelope and is not a promotion gate.
This is a measured envelope for this machine/workload, not a universal guarantee
against arbitrary scheduler pauses. Qualification must be repeated after a
material runtime/host change.

## Hypotheses separated

- Simulator/interface timing: demonstrated timeout, old-action hold and FIFO
  backlog. Eliminating in-loop disk I/O eliminates the tested divergence.
- Controller sample-time sensitivity: no evidence of a defect within this
  envelope. Unchanged controller and simulated-time rate limits reproduce the
  exact trace in ordinary, delayed and GUI cases. No damping/steering law was
  changed to solve timing.
- Candidate margin sensitivity: still real. A perturbed state can violate the
  narrow .6 local gate, but the prescribed 2 ms itself does not require slower
  driving once the interface meets its deadline.
- Wall-time RNG seeding exists in SCR, but is not required to explain this
  failure: different launch times and delay distributions produce identical
  traces after the I/O correction. No seed or RNG behavior was changed.

Subsequent performance campaigns use the corrected interface. Their fastest
single laps are experimental until separately requalified.

## Startup snapshot correction (20:03 UTC)

The evolutionary campaign's 40-evaluation reference guard halted at
`20260924T200044_277720Z_mapped-v2`: 96.362 s, max |trackPos| .609404,
failed local margin gate. Installed assets were unchanged. The first differing
sensor was packet 2 (RPM 942.478 instead of 1100.33), before movement.
Measured receive-to-send latency never exceeded .797 ms, but that measurement
excludes work before the first receive. The harness still read process metadata
and wrote `runtime_maps.txt` after the SCR identification handshake. This is a
startup deadline hazard consistent with the observed first-action loss; the
failed run did not have the server observer enabled, so its timeout is inferred,
not directly observed.

`timing_experiment.py` now captures the command before identification and saves
process mappings only after the final command, before terminating its own TORCS.
No driving law, simulator flag, physics asset or validity criterion changed.
Two immediate pre-fix diagnostic reruns and three post-fix reference runs matched
95.310 exactly. Three post-fix ATLAS runs matched 85.244 and its full trajectory.
All six post-fix runs had zero active server timeouts with the observation-only
shim (`audit/startup_recheck.json`). An AST regression now checks that process
snapshot reads/writes cannot reappear between identification and loop teardown.
The seeded search resumed its persisted 40 evaluations, rather than discarding
or rerunning them. This correction addresses the identified startup I/O hazard;
it does not promise immunity to arbitrary OS scheduling stalls.

A second guard (`20260924T200641_897878Z_mapped-v2`) caught a mid-lap
10.888 ms receive-to-send pause at packet 1306; eventual trajectory drift began
at packet 1326. The lap was 96.214 and locally valid but did not reproduce the
reference. This is a separate stall, not proof that the startup write remained.
Its host/GC cause is not established. The harness now collects cyclic garbage
before identification, disables cyclic collection during its bounded active
exchange, and restores the prior setting after shutting down its simulator.
Reference-count disposal remains active. Packet records/controller state are
acyclic; campaign history is no longer traversed by automatic cyclic GC during
commands. Three observed reference reruns match 95.310 with no active timeouts;
see `audit/gc_boundary_recheck.json`. This does not eliminate arbitrary host
preemption and full timing qualification remains mandatory.

The asynchronous writer now completes a warm-up message round trip before SCR
identification, so creation of Python's multiprocessing queue feeder thread
cannot be deferred to the first post-command telemetry enqueue. The standalone
client uses ATLAS and preserves the exact input parameters (including launch
parameters consumed by the subclass) in its manifest. Timing qualification now
also runs the actual asynchronous output worker, not only buffered raw logging.
