# Setup and reproduction

## Offline, without TORCS

Run `python qualify_atlas.py --offline` from the repository root. This compiles
the Python files and runs the real unit/replay tests. Success explicitly reports
`OFFLINE_PASS_NOT_RACE_QUALIFIED`; it does not claim a new simulator result.
The selected packet fixtures are required test data, not fresh simulation runs.

Optional plot regeneration requires NumPy and Matplotlib; install
`requirements-analysis.txt` only if needed. Then run:

```sh
python plot_atlas_evidence.py experiments/20260925T010629_515431Z_atlas-v1
```

## Measured simulator environment

The benchmark was measured with Python 3.10 in an existing Linux TORCS/SCR
container. The harness expects the simulator at `/usr/local/torcs`, its libraries
at `/usr/local/torcs/lib/torcs`, data at `/usr/local/torcs/share/games/torcs`, X
display `:1`, and a configured practice template at
`/home/student/.torcs/config/raceman/practice.xml`. These are measured environment
assumptions, not a claim that an arbitrary TORCS installation reproduces RC1.

Obtain the competition-approved simulator, physics, car and livery through the
competition distribution. This repository neither downloads nor replaces them.
The qualification report records the exact installed file hashes. A mismatch
must be investigated rather than bypassed to obtain a PASS.

## Standing-start GUI run

Select Practice → Corkscrew, scr_server 1 (driver index 0), initial speed zero,
with the prescribed original car and livery. The controller attaches to SCR on
localhost UDP port 3001. Start `python competition_client.py --params
atlas_params.json`, then start the GUI race. Ctrl+C closes/drains telemetry.
Do not enable the historical full-screen IBM debug display.

For a reproducible, isolated GUI evidence run in the measured environment:

```sh
python timing_experiment.py --controller atlas-v1 --params atlas_params.json --max-steps 20000 --buffer-logging --async-logging --gui
```

Use the normal TORCS menus to start the prepared Practice session. The harness
owns only the simulator it launched, preserves a project-local configuration,
and stops after the first completed standing-start lap. Its `RUN` line gives
the evidence directory. Run the authoritative final gate with that directory:

```sh
python qualify_atlas.py --params atlas_params.json --gui-run experiments/ACTUAL_RUN_ID
```

This runs the timing battery; do not repeat it for ordinary exploratory tuning.
`--max-lap-time` sets a strict promotion target and defaults to 85.0 seconds.
The local gate requires completion, a standing start, zero damage, all track
sensors on road, |trackPos| ≤ .6, complete evidence and unchanged installed assets.
It is not a replacement for the organizer's full submission rules.

## Release generation

Run `python tools/generate_release.py` once the qualified candidate is selected.
It verifies packaged control sources, parameters and map against the preserved
checkpoint, then generates the benchmark table and submission manifest.
Run `--manifest-only` after committing/tagging to bind an untracked distribution
manifest to that exact source commit without creating a self-referential commit.
Pass `--video URL` only after the official video has been captured and checked
against the selected source. Do not mark a video complete merely by providing a URL.
