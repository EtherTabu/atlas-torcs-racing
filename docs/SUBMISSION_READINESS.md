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
| Official video | **Pending.** Capture a clean normal GUI standing-start run of the selected candidate. No engineering overlay in the official video unless the organizer explicitly permits it. |
| Source/video consistency | **Pending video.** Record selected Git commit/tag, control/parameter/map hashes and video identifier together; verify they refer to the same candidate. |
| Final commit/tag and manifest | Local source commit and generated manifest required before publication; no claim that historical evidence was recorded from a later Git commit. Bind byte-identical source using hashes. |
| License and attribution | Existing source notices retained. Do not apply the code's MIT license to the livery or independently licensed simulator assets. Confirm livery redistribution terms. |
| Official submission procedure | **Human confirmation required:** deadline, upload destination, video specification and any organizer rules not supplied here. |

Final submission is not complete while the public repository, official video,
source/video consistency, or organizer-confirmation rows remain pending.
