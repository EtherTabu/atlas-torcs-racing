# Official-video preparation — frozen ATLAS RC1

Status: workflow prepared; no new video or simulator run has been made.
The selected candidate remains 84.388 s with the preserved nine-run timing PASS
and identical normal GUI trajectory. This workflow is a project procedure, not
an assertion about the organizer's required video format.

1. Resolve organizer video requirements from the submission brief. Use the
   existing qualified Linux TORCS/SCR GUI environment. Record the packaging Git
   commit and compare controller, parameter, map, livery and installed asset hashes
   with the preserved evidence before capture. Keep the existing race configuration.
2. Prepare screen recording outside the SCR client. Capture the simulator viewport
   clearly, including the standing start and completed lap time; exclude unrelated
   desktop content. Test recorder availability without launching TORCS. Recorder
   load is a possible timing regression, so the resulting trace must be checked.
3. Reuse the qualified GUI harness, from the release repository root:

   ```sh
   python timing_experiment.py --controller atlas-v1 --params atlas_params.json --max-steps 20000 --buffer-logging --async-logging --gui
   ```

   Start recording before using the normal Practice/New Race menu for the already
   configured Corkscrew/scr_server 1 session. Do not change controller, parameters,
   livery, car physics, race configuration or simulator flags. Do not inject delays,
   enable IBM debug, or invoke `qualify_atlas.py`'s nine-run battery for the video.
4. Preserve the new run directory and original capture. Check its lap, validity,
   source/parameter/map/asset/race configuration identities, complete telemetry and
   trajectory against the preserved GUI evidence. Expected full-trajectory SHA-256:
   `1f0d7f806201920aa2979450588ccf61f4b3d624dce0aecb10bc5ba8d3c3ef60`.
   Expected lap: **84.388 s**, zero damage, max abs(trackPos) **0.583837**.
   A mismatch is evidence to investigate; do not relabel a different run as RC1's
   qualified result. Only regression evidence can justify additional qualification.
5. Review the video visually for start, continuity, readable result and correct car.
   Bind the actual video filename/hash (and final URL when available), capture run,
   packaging commit and preserved qualification hashes in the submission manifest.
   A supplied URL alone is not a consistency check. Keep large video files outside
   the Git source history; use the organizer-approved delivery method.
6. Only after the official video and final consistency review are complete, create
   the final release/tag. Publish no claim of complete submission while the checklist
   still contains unresolved organizer requirements.

## Presentation boundary

Use original installed track textures for the official capture. Branded banner
copies under presentation/ are separate engineering-showcase material only. The
IBM guide permits banner texture customization but does not explicitly establish
its use in official fastest-lap footage. Do not install the showcase copy for the
official run. No engineering overlays belong in the official capture workflow.
