# RC1 source/video consistency record

Status: **PASS**, verified on 2026-09-25 by Codex through automated identity and
timestamp checks and visual frame review. Qualification evidence is unchanged.

## Frozen candidate before capture

| Field | Required value |
|---|---|
| Controller | `atlas_controller.py` SHA-256 `3f04a590c1ce72d1ff29adb6b4dd73a6bd649eac31ce3764e25ce7fa59784be5` |
| Parameters | `atlas_params.json` SHA-256 `c6ac84014112edc203db0c5995e439a78af07137601ea3152bb9cedb6cad72a9` |
| Track model | `track_model.json` SHA-256 `eea1b611a1d99a8921140abe4568e7985e2e0c6f726c7b62c151d5145294917f` |
| Livery | `car1-trb1.rgb` SHA-256 `05bc6e7f24528cc66ca01358ec9ba78427b5ed413d7f5471c2e775bb2de0987c` |
| Expected trajectory | `1f0d7f806201920aa2979450588ccf61f4b3d624dce0aecb10bc5ba8d3c3ef60` |
| Qualified measurement | 84.388 s; zero damage; max abs(trackPos) 0.583837 |
| Video environment | Stock Corkscrew textures, scr_server 1, standing start, normal GUI |

## Verified capture

| Field | Value |
|---|---|
| Capture-source commit | `3427a92e8604fc14e88c99afb1d47ccb301f3a88` |
| Packaging commit | Actual final revision is recorded in the generated release `submission_manifest.json`; distinct from capture-source commit. |
| Capture run directory | `experiments/20260925T151614_884743Z_atlas-v1` |
| Preferred video | `dist/final-release/ATLAS-RC1-submission-candidate.mp4` |
| Candidate SHA-256 | `0772657c069b61e887a10bc757138f47c40399fd5ff95d43debd745eee2e8ba4` |
| Distribution | Final tag `atlas-rc1-final`; [release assets](https://github.com/EtherTabu/atlas-torcs-racing/releases/tag/atlas-rc1-final) once published. |
| Observed lap, damage, max abs(trackPos) | 84.388 s, zero damage, 0.583837 |
| Source/parameter/map/livery hashes match | PASS; full runtime hashes in [official_video.json](../evidence/official_video.json). |
| Track and race configuration match | All 197 installed assets match checkpoint before/after capture; stock Corkscrew, unchanged dynamics. Race XML byte-identical to qualified GUI. |
| Race configuration SHA-256 | `c20af215d6b5d286ccf345f2f6246640af70f828a6364813002782de4b587271` |
| Qualification report SHA-256 | `db825cbe79ee85bb34ff8191db08fd9824cb16d632250960b6c7b7fed77d4704` |
| Checkpoint SHA-256 | `c4c1477cafc9d3451b76de30fad129f7b200c28deaaf6ef74ee2c98ad1144c2b` |
| Trajectory | Exact qualified SHA-256 above; all seven local validity checks PASS. TORCS supplies no separate official validity flag. |
| Visual review | Before/at standing start, early, middle, late lap and genuine completion reviewed; full start/completion and HUD preserved. |
| Reviewer/date | Codex, 2026-09-25 |

## Three distinct videos

The untouched RAW provenance source is `2edbd66db06f_1 - noVNC - Google Chrome 2026-09-25 11-16-00.mp4`, retained locally in Windows Videos/Captures: 174.036767 s, 166720608 bytes, SHA-256 `39ebbabfe7dedd142ff5d8d1d5d31c8dd83f813291071aa1c3a736b637d4acaf`. It contains browser/desktop UI and browsing-context labels and is not a public release asset.

The **preferred organizer-facing candidate**, subject to organizer rules, is 87.901867 s, 1006 x 754, 37430884 bytes, silent. RAW timestamps [81,168.92) were retained with crop 1006:754:8:240 and a constant timestamp offset only. All **1,252 retained frames** preserve RAW relative timestamps exactly at time base 1/30000, with **zero deviation** and unchanged **1x speed**. First/last RAW PTS: 2430515 / 5066571 ticks. No artificial hold, overlays, branding, transitions, scaling or reconstructed pixels.

Chrome tabs/address/bookmarks, XFCE/window chrome, desktop, scrollbars and blue Computer Use outline are absent. The small noVNC handle and mouse pointer remain intentionally to preserve genuine viewport/HUD pixels. Genuine completion appears for its native duration; HUD shows `01:24:38` (hundredths), while SCR `lastLapTime` is 84.388.

The separate **presentation-only** `dist/final-release/ATLAS-RC1-official-lap.mp4` has a five-second held completion frame: 95.966667 s, 1000 x 750, 37560213 bytes, SHA-256 `256a0e7f6d506226e0285c4cd32a3e0ddd977a366893cde18773bf1aadcdb6f9`. It is not the recommended submission video.

Recorded-run archive: `ATLAS-RC1-recorded-run.zip`, SHA-256 `f93d6d04a6fdd32e54b0c8c1a6f0629d3b1dbebcf0e691b1ff7b6dd0015f6510`. Recorded-run file hashes and full source identity are bound in `official_video.json`.

Generate the final distribution manifest after the final documentation commit to avoid a self-referential commit. IBM course completion, organizer deadline/format confirmation and final organizer upload remain human-only items.
