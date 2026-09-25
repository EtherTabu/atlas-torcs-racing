# Submission readiness

This checklist records requirements stated by the project owner and demonstrated
engineering evidence. It does not invent additional organizer rules. The exact
official deadline, required video format and final upload procedure are not in
the available evidence and require human confirmation against the official rules.

| Check | Current evidence / remaining action |
|---|---|
| Public GitHub repository | Local curated tree prepared; remote publication pending. Intended repository: `EtherTabu/atlas-torcs-racing`, never the profile repository `EtherTabu/EtherTabu`. |
| AI controller code included | Present; selected runtime source hashes must match generated manifest. |
| Required car livery included | `assets/livery/car1-trb1.rgb` copied byte-for-byte from SCR driver index 0. Provenance and hash included. |
| Official livery unchanged | Local identity verified against qualification hashes. Human confirmation still needed that this installed asset is the organizer-required livery and may be redistributed publicly. |
| Car dynamics unchanged | Qualification preserves installed car, track and physics hashes. No model dynamics are distributed as modified assets. |
| Corkscrew | Recorded race configuration and complete trace identify the selected track. |
| Standing start | First sensor: distRaced 0, speed effectively zero; official lap timer used. |
| Fastest qualified lap | Generated from the selected checkpoint; experimental Frontier laps cannot replace it without qualification. |
| Timing and GUI qualification | Preserved PASS report; nine identical timing repeats and matching normal GUI trace for RC1. Requalify changed driving/runtime artifacts or a new final candidate. |
| Official video | **Pending.** Capture a clean normal GUI standing-start run of the selected candidate. A clean capture without engineering overlays is our presentation recommendation, not a verified organizer rule. |
| Source/video consistency | **Pending video.** Record selected Git commit/tag, control/parameter/map hashes and video identifier together; verify they refer to the same candidate. |
| Final commit/tag and manifest | Packaging history and manifest exist; refresh the manifest after the final packaging commit. Create no final release/tag until video consistency is checked; no claim that historical evidence was recorded from a later Git commit. Bind byte-identical source using hashes. |
| License and attribution | Existing source notices retained. Do not apply the code's MIT license to the livery or independently licensed simulator assets. Confirm livery redistribution terms. |
| Official submission procedure | **Human confirmation required:** deadline, upload destination, video specification and any organizer rules not supplied here. |

Final submission is not complete while the public repository, official video,
source/video consistency, or organizer-confirmation rows remain pending.

## Evidence authority and publication blocker

Project-owner instructions establish the requested public repository, controller
code, required unchanged livery, unchanged car dynamics, Corkscrew standing start,
and official video. The qualification report verifies the local engineering facts;
it does not authenticate organizer rules. No organizer rulebook, submission brief,
or asset redistribution grant was found in the available project material. The
upstream Gym-TORCS README and MIT license do not establish artwork permission.

**Single unresolved organizer question:** can the organizer's original submission
brief or asset terms confirm that the packaged `car1-trb1.rgb` is the required
livery and may be included in the public GitHub entry? If the same brief specifies
the deadline, video format or upload procedure, use those exact requirements.
Until this is resolved, retain the asset locally and do not publish this history,
which already includes it. Do not substitute or alter the qualified livery.

See [the video workflow](VIDEO_WORKFLOW.md). No new simulator runs are needed for
repository preparation. Authentication can wait until this publication blocker is
resolved; do not collect tokens in chat.
