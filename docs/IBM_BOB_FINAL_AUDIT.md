# ATLAS RC1 — IBM Bob Independent Final Release Audit

**Audit date:** 2026-09-25  
**Auditor:** IBM Bob (independent engineering review)  
**Scope:** Release repository at `EtherTabu/atlas-torcs-racing`, current HEAD `d02132a`  
**Immutable artefacts inspected:** `atlas_controller.py`, `atlas_params.json`, `track_model.json`, `assets/livery/car1-trb1.rgb`, `evidence/qualification.json`, `evidence/qualified_checkpoint.json`

---

## PASS

### P-01 — Repository identity and purpose are clearly stated

`README.md` opens with the full name, acronym expansion, competition context, engineering strategy and performance claim. The tagline "HUMAN LED AI ACCELERATED RACE PROVEN" is consistent across `README.md`, `presentation/README.md` and the artwork. No ambiguity about the project's purpose or origin.

---

### P-02 — RC1 lap-time claim is internally consistent across all machine-readable evidence

The claimed 84.388 s result is asserted identically in:

| Source | Value |
|---|---|
| `README.md` | 84.388 s |
| `evidence/qualification.json` → `lap_time_s` | 84.388 |
| `evidence/qualified_checkpoint.json` → all four `benchmark_categories` fields | 84.388 |
| `dist/submission_manifest.json` → `official_lap_time_s` | 84.388 |
| All 9 `runs[*].analysis.lap_time_s` in `evidence/qualification.json` | 84.388 |
| `experiments/20260925T010713_126466Z_atlas-v1/analysis.json` (GUI run) | 84.388 |

All nine qualification runs in `evidence/qualification.json` also carry the same trajectory SHA-256: `1f0d7f806201920aa2979450588ccf61f4b3d624dce0aecb10bc5ba8d3c3ef60`.

---

### P-03 — Zero-damage and trackPos claims are supported by machine-readable evidence

Every run record in `evidence/qualification.json` records `damage_increase: 0.0` and `max_abs_trackPos: 0.583837`, within the declared 0.6 local gate. The `validity_checks.no_damage` and `validity_checks.conservative_track_margin` flags are `true` in all nine runs. The GUI run analysis matches identically.

---

### P-04 — Immutable artefact SHA-256 values verified by independent computation

The following hashes were independently computed from the current workspace files and confirmed to match all assertions in `README.md`, `evidence/qualification.json`, `evidence/qualified_checkpoint.json`, `dist/submission_manifest.json`, and the checkpoint's `source_sha256` dictionary:

| File | Verified SHA-256 |
|---|---|
| `atlas_controller.py` | `3f04a590c1ce72d1ff29adb6b4dd73a6bd649eac31ce3764e25ce7fa59784be5` |
| `atlas_params.json` | `c6ac84014112edc203db0c5995e439a78af07137601ea3152bb9cedb6cad72a9` |
| `track_model.json` | `eea1b611a1d99a8921140abe4568e7985e2e0c6f726c7b62c151d5145294917f` |
| `assets/livery/car1-trb1.rgb` | `05bc6e7f24528cc66ca01358ec9ba78427b5ed413d7f5471c2e775bb2de0987c` |

The qualification report itself (`evidence/qualification.json`) hashes to `db825cbe79ee85bb34ff8191db08fd9824cb16d632250960b6c7b7fed77d4704`, matching the `qualification_report_sha256` recorded in `evidence/qualified_checkpoint.json`. All cross-references are consistent.

---

### P-05 — Documented control architecture agrees with source code

`docs/ARCHITECTURE.md` describes: curvature-limited speed planning, backward braking propagation, smoothstep line targets, heading and position feedback, curvature feedforward, steering rate limits, wheel-speed traction and brake-lock feedback, RPM gear shifts, and a simulation-time clutch launch. All of these are directly traceable to `experimental_controller.py` (the parent) and `atlas_controller.py` (launch extension). The architecture note that "velocity-heading and steering-cap features default to disabled" is confirmed by `atlas_params.json` (neither `velocity_heading_weight` nor `steer_cap` keys are present, leaving them at defaults of 0 and 1 respectively). No claims in the architecture document contradict the code.

---

### P-06 — Nine timing qualification runs with three distinct timing conditions are present and correctly described

`evidence/qualification.json` contains exactly nine runs: three `ordinary`, three `fixed3ms`, three `gui_resampled`. The `README.md` claim of "nine timing qualification runs" is accurate. The `TIMING.md` description of the three conditions (ordinary headless, +3 ms fixed delay, seeded GUI jitter replay) agrees with the run labels. All nine produce identical trajectories, 84.388 s, zero damage.

---

### P-07 — GUI reproduction is present and matches the timing qualification trajectory

`experiments/20260925T010713_126466Z_atlas-v1/analysis.json` confirms `lap_time_s: 84.388`, `trajectory_sha256: 1f0d7f8...`, `local_validity: passed`. This is the GUI run referenced by `evidence/qualification.json` (`gui_run`) and `evidence/qualified_checkpoint.json`. The qualification checks `gui_valid`, `gui_same_trajectory`, `gui_same_parameters`, `gui_normal_mode`, `gui_same_assets`, `gui_same_control_sources` are all `true`.

---

### P-08 — Source code inheritance is transparent and correct

`atlas_controller.py` explicitly imports `from experimental_controller import Driver as SpatialDriver` and defines `Driver(SpatialDriver)`. The inheritance chain is visible, documented in `docs/ARCHITECTURE.md`, and correctly describes the relationship. `experimental_controller.py` imports `from racing_controller import clamp`, which is the third level. The entire stack is present in the repository.

---

### P-09 — Livery identity and redistribution basis are carefully documented

`docs/LIVERY_PROVENANCE.md`, `assets/livery/provenance.json`, `NOTICE.md` and `docs/SUBMISSION_READINESS.md` all consistently state: the livery is an unchanged copy of the competition-qualified asset; IBM competition documentation requires public inclusion; no broader artwork license is asserted. The file hash `05bc6e7f...` is consistent across the livery file, its provenance record, the qualification asset hashes, and the submission manifest. The `modified: false` flag in `assets/livery/provenance.json` is correct.

---

### P-10 — Credential, secret, and private machine path audit is clean

No credentials, tokens, API keys, or private identifiers were found in any tracked file. The only personal-looking path in tracked `.py` files is `/home/student/` in `race_experiment.py` (line 51) and `timing_experiment.py` (line 53); this is the well-documented competition container user path, not a developer's machine path. `docs/REPRODUCTION.md` explicitly documents these as intentional measured-environment provenance. The container image reference in `docs/LIVERY_PROVENANCE.md` (`docker.io/johnsloe/torcs-competition:amd64`) is public competition infrastructure, not private credentials.

---

### P-11 — Offline CI gate is correctly scoped and clearly labelled

`.github/workflows/offline.yml` runs compile, `qualify_atlas.py --offline`, and `generate_release.py --manifest-only`. The offline gate reports `OFFLINE_PASS_NOT_RACE_QUALIFIED` (confirmed in `qualification_reports/20260925T092418_088529Z/report.json`), not a full race PASS. The distinction is explicit in the code and documentation. Cloud CI does not claim a simulator result it cannot produce.

---

### P-12 — Progression table and historical checkpoints are presented with appropriate evidence levels

The `README.md` benchmark table and `generate_release.py` hardcode the four checkpoints with accurate evidence levels: "Audited historical" for the 252.856 baseline, "Repeated reference" for 95.310, "Timing + GUI" for 89.394 and RC1. The README text explicitly states "Historical checkpoints do not all carry RC1's qualification level." `docs/TIMING.md` carries a prominent header note clarifying it is a historical investigation record and that the final evidence is `evidence/qualification.json`.

---

### P-13 — No prohibited simulator flags are present in any qualification run

All manifests in the six bundled experiment directories were checked by the qualification gate against the forbidden set `{'-nodamage', '-nofuel', '-nolaptime', '-noisy'}`. The qualification check `prohibited_flags_absent: true` is asserted. This is enforced programmatically in `qualify_atlas.py` (lines 65–66) and line 102 for the GUI run.

---

### P-14 — Release generation tool verifies source integrity before writing

`tools/generate_release.py` refuses to proceed if `evidence/qualification.json` is not a full PASS, if the qualification report hash differs from the checkpoint, if any runtime source hash differs from the qualified candidate, or if the livery file hash differs from its provenance record. The `submission_ready: false` and `pending` fields are hardcoded in the tool — the manifest cannot self-certify as complete.

---

### P-15 — Security and `.gitattributes` treatment of binary files is correct

`.gitattributes` sets `* -text` to prevent line-ending conversion on all files, preserving the qualified binary and source hashes across Windows and Linux checkouts. This is necessary for hash reproducibility.

---

### P-16 — No performance manipulation techniques present

`atlas_params.json` contains no references to prohibited flags. The controller code contains no sleep manipulation, clock overrides, simulator patching, or asset modification. Speed planning uses documented `sqrt(a/|k|)` formulas. The gate requires the TORCS `lastLapTime` sensor value, not a wall-clock estimate.

---

## WARN

### W-01 — `qualified_checkpoint.json` references a qualification report path that does not exist in the public repository

`evidence/qualified_checkpoint.json` → `"qualification_report": "qualification_reports/20260925T010958_141539Z/report.json"`. This directory is absent from the repository (it is excluded by `.gitignore`).

**Mitigating factors:** The SHA-256 of the referenced file (`db825cbe...`) is independently verifiable by hashing `evidence/qualification.json`, which is present, tracked, and matches exactly. `docs/TIMING.md` notes that `audit/` and local lab IDs are in the retained local laboratory. The discrepancy does not affect evidence integrity but will confuse a reader who attempts to follow the path.

---

### W-02 — `submission_manifest.json` `source_commit` is one commit behind HEAD

`dist/submission_manifest.json` records `source_commit: 20e1a2f9f9...`. Current HEAD is `d02132a`. The difference is one commit that modified `README.md`, `README.template.md`, and `tools/generate_release.py` (a line-ending fix). None of the runtime sources or evidence artefacts changed. The manifest is not tracked by git and is regenerated by CI; the CI workflow runs `generate_release.py --manifest-only` and produces a fresh manifest on every push, so the published CI artefact should be current. However, the locally committed version is stale by one commit.

**Action recommended:** Re-run `python tools/generate_release.py --manifest-only` after confirming HEAD is the final packaging commit, and ensure the published CI artefact is used as the submission manifest.

---

### W-03 — Encoding mojibake in `tools/generate_release.py` and generated `README.md`

The string literal `'pending — not submission-complete'` in `tools/generate_release.py` (line 69) and the generated `README.md` (line 134) contain Windows-1252 mojibake: the UTF-8 bytes for the em dash (U+2014, `\xe2\x80\x94`) were re-encoded as if Latin-1/Windows-1252, producing the three-byte sequence `\xc3\xa2\xe2\x82\xac\xe2\x80\x9d` (rendered by some decoders as `â€"`). The result is visually legible in browsers that decode the page as UTF-8 but is not a clean em dash. GitHub renders Markdown as UTF-8, so visitors will see `â€"` rather than `—` in that sentence.

**This affects only the video-pending notice string** — it has no impact on any hash, evidence, or race result.

**Action recommended:** Replace the mojibake sequence with a clean ASCII hyphen `--` or correct UTF-8 em dash in `tools/generate_release.py` and regenerate `README.md`.

---

### W-04 — `TIMING.md` "9/9, all 89.394" refers to the earlier spatial candidate, not RC1

`docs/TIMING.md` states "Candidate: **9/9**, all 89.394 with the original trace hash." This is the qualification result for `experimental-v3` (the spatial candidate), performed during the timing correction investigation. RC1 later achieved 84.388. The historical note at the top of the file clarifies that it is an investigation record, but a reader skimming the file could confuse this 9/9 with RC1's 9/9 at 84.388.

**Mitigating factor:** The header blockquote explicitly redirects to `evidence/qualification.json`. No false claim is made; the context establishes this was an earlier candidate.

---

### W-05 — `best_params.json` and `candidate_v3_params.json` are present but undocumented

Two non-selected parameter files (`best_params.json`, `candidate_v3_params.json`) are tracked in the repository with no README or inventory entry explaining their purpose or relationship to RC1. They differ from `atlas_params.json`. A reader cannot determine whether these represent earlier candidates, failed experiments, or abandoned improvements.

**Mitigating factor:** The repository states that it contains the qualified racer and representative audit evidence, and that raw experimental lab material is excluded. These files do not affect any hash check or qualification gate.

---

### W-06 — `docs/SUBMISSION_READINESS.md` records "Public repository publication" as a pending row while `docs/PUBLICATION.md` records the repository as already live

`docs/SUBMISSION_READINESS.md` (and the hardcoded `pending` list in `dist/submission_manifest.json`) includes "Public repository publication." `docs/PUBLICATION.md` states: "The public remote is live at `https://github.com/EtherTabu/atlas-torcs-racing`." This is an internal tracking inconsistency. The checklist row was never closed after publication.

---

### W-07 — `git_commit` is `null` in `evidence/qualification.json` and `evidence/qualified_checkpoint.json`

Both files carry `"git_commit": null`, meaning the full qualification run was executed before the qualifying commit was recorded. The `dist/submission_manifest.json` correctly explains this with `"provenance_note"` and supplies the packaging commit separately. However, the qualification evidence itself cannot be traced to a specific Git revision by hash. This is a process observation, not a fabrication concern; the source hashes in the checkpoint are independently verified against the current files.

---

## ACTION REQUIRED

### A-01 — Official video is absent; `SOURCE_VIDEO_CONSISTENCY.md` is entirely unpopulated

`docs/SOURCE_VIDEO_CONSISTENCY.md` is a template with all "Fill only after capture" fields marked "Pending." `docs/SUBMISSION_READINESS.md` lists "Official video" as pending. The `submission_manifest.json` has `"video": null` and `"submission_ready": false`.

**IBM SkillsBuild requires a fastest standing-start Corkscrew video as a submission artefact.** Without it, submission cannot be complete. `docs/VIDEO_WORKFLOW.md` contains a ready-made capture procedure. This is the single largest remaining blocker.

**Required action:** Capture the official video per `docs/VIDEO_WORKFLOW.md`, verify the new run trace matches the frozen trajectory SHA-256 `1f0d7f8...`, fill in `docs/SOURCE_VIDEO_CONSISTENCY.md`, and update `dist/submission_manifest.json` with the video URL before final submission.

---

### A-02 — IBM SkillsBuild course completion is unconfirmed

`docs/SUBMISSION_READINESS.md` states: "All team members finish IBM Granite Models for Software Development — Participant completion needs human confirmation." IBM requires all team members to have completed this course.

**Required action:** Confirm and document course completion for all participating team members before submission.

---

### A-03 — Submission manifest is stale by one commit and is not committed

`dist/submission_manifest.json` is in `.gitignore` and is therefore absent from the published Git repository. It records `source_commit: 20e1a2f` while HEAD is `d02132a`. At final submission, the manifest must reflect the exact HEAD commit and must be provided through the submission mechanism (not necessarily committed, but must match).

**Required action:** Run `python tools/generate_release.py --manifest-only` after the final packaging commit (including after the video is confirmed), and use the resulting manifest for submission. Do not submit the manifest generated from a pre-final commit.

---

### A-04 — Final release/tag has not been created

`docs/PUBLICATION.md` and `docs/SUBMISSION_READINESS.md` both state "No final release/tag before video consistency review." The CI and submission process are consistent in deferring this. Once the video is captured and verified, a final release/tag must be created to bind the submitted artefacts to an immutable Git reference.

**Required action:** After video verification and manifest refresh, create a final Git tag (e.g. `rc1-final`) and GitHub release, and confirm the public repository reflects the exact submission state.

---

### A-05 — Organizer submission procedure, deadline, and video format require human confirmation

`docs/SUBMISSION_READINESS.md` states: "Official submission procedure — Human confirmation required: deadline, upload destination, video specification and any organizer rules not supplied here." None of the repository evidence includes the IBM SkillsBuild submission deadline or upload URL.

**Required action:** Consult the official IBM SkillsBuild competition brief directly to confirm the submission deadline, required video format, upload destination, and any rules not captured in the supplied evidence screenshots.

---

## Cross-check summary

| Claim | Evidence checked | Result |
|---|---|---|
| 84.388 s lap time | 9/9 runs in `evidence/qualification.json`, GUI run analysis, checkpoint, manifest | Consistent |
| Zero damage | All run records `damage_increase: 0.0` | Consistent |
| max\|trackPos\| 0.583837 | All run records | Consistent |
| 222.248 km/h peak speed | All run records | Consistent |
| 9 timing repeats | Count of runs in qualification.json | Confirmed: 9 |
| GUI reproduction | GUI run analysis matches trajectory SHA | Confirmed |
| Controller SHA matches README | Independent hash computation | Match |
| Params SHA matches README | Independent hash computation | Match |
| Track model SHA matches README | Independent hash computation | Match |
| Livery SHA matches all provenance records | Independent hash computation | Match |
| Qualification report SHA matches checkpoint | Independent hash computation | Match |
| No prohibited flags | Qualification gate check = true | Confirmed |
| Architecture matches source | Line-by-line source review | No contradictions found |
| No credentials or private paths | Pattern search across all tracked files | None found |
| All README links resolve | Path existence check | All 14 links resolve |

---

## How IBM Bob was used

IBM Bob was used in this phase exclusively as an independent release auditor. Specifically:

- Systematically read and cross-checked all repository files including `atlas_controller.py`, `atlas_params.json`, `track_model.json`, all documentation under `docs/`, all qualification evidence under `evidence/`, the submission manifest, the `.github/` CI workflow, experiment fixtures, and the release tooling.
- Independently computed SHA-256 hashes of the four immutable artefacts (`atlas_controller.py`, `atlas_params.json`, `track_model.json`, `assets/livery/car1-trb1.rgb`) and verified them against all claims in the README, qualification report, checkpoint, and manifest.
- Cross-checked the qualification evidence structure (run counts, trajectory hashes, lap times, validity flags) against all README claims without accepting README prose as proof.
- Inspected the control architecture description against the actual Python source code.
- Identified and characterized the encoding mojibake in `tools/generate_release.py` and the generated `README.md`.
- Verified all README internal links for existence.
- Checked for credentials, private machine paths, and sensitive information across all tracked files.
- Identified the stale manifest commit, the missing qualification report path, and the unresolved submission pending items.
- Produced this audit report.

All racing results, controller design, parameter optimization, and qualification evidence existed before this audit.
