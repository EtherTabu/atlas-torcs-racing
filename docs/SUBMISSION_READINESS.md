# Submission readiness

This checklist combines the authoritative IBM SkillsBuild submission screenshot
with demonstrated engineering evidence. See [requirement and livery evidence](LIVERY_PROVENANCE.md). The exact
official deadline, required video format and final upload procedure are not in
the available evidence and require human confirmation against the official rules.

| Check | Current evidence / remaining action |
|---|---|
| Public GitHub repository | Published public repository: `EtherTabu/atlas-torcs-racing`, separate from the profile repository `EtherTabu/EtherTabu`. |
| AI controller code included | Present; selected runtime source hashes must match generated manifest. |
| Required car livery included | `assets/livery/car1-trb1.rgb` copied byte-for-byte from SCR driver index 0. Provenance and hash included. |
| Official livery unchanged | Local identity verified against qualification hashes. Public inclusion is explicitly required by IBM. Identity resolved by IBM Customising Guide: car1-trb1.rgb, default slot 1, SCR index 0; exact qualified bytes preserved. |
| Car dynamics unchanged | Qualification preserves installed car, track and physics hashes. No model dynamics are distributed as modified assets. |
| Corkscrew | Recorded race configuration and complete trace identify the selected track. |
| Standing start | First sensor: distRaced 0, speed effectively zero; official lap timer used. |
| Fastest qualified lap | Generated from the selected checkpoint; experimental Frontier laps cannot replace it without qualification. |
| Timing and GUI qualification | Preserved PASS report; nine identical timing repeats and matching normal GUI trace for RC1. Requalify changed driving/runtime artifacts or a new final candidate. |
| Official video | **Pending.** Capture a clean normal GUI standing-start run of the selected candidate. A clean capture without engineering overlays is our presentation recommendation, not a verified organizer rule. |
| Source/video consistency | **Pending video.** Use the frozen [source/video record](SOURCE_VIDEO_CONSISTENCY.md); bind the actual capture to the RC1 hashes. |
| Final commit/tag and manifest | Packaging history and manifest exist; refresh the manifest after the final packaging commit. Create no final release/tag until video consistency is checked; no claim that historical evidence was recorded from a later Git commit. Bind byte-identical source using hashes. |
| License and attribution | Existing source notices retained. Do not apply the code's MIT license to the livery or independently licensed simulator assets. IBM requires livery inclusion for this submission; no broader artwork license is asserted. |
| Official submission procedure | **Human confirmation required:** deadline, upload destination, video specification and any organizer rules not supplied here. |

Final submission is not complete while the public repository, official video,
source/video consistency, or organizer-confirmation rows remain pending.


| Additional verified IBM requirement | Status |
|---|---|
| All team members finish IBM Granite Models for Software Development | Participant completion needs human confirmation. |

## Livery resolved

IBM competition documentation establishes the car1-trb1 driver livery and default
slot; IBM submission instructions require public inclusion and unchanged official
submission livery. [Provenance](LIVERY_PROVENANCE.md) binds this to RC1's exact asset.
The alternate car1-ow1 configuration is not a release blocker.

## Presentation checkpoint

Public repository, AI source, required livery and IBM livery identity evidence are
present. RC1's car dynamics, track model, Corkscrew standing-start configuration and
all 83 immutable checkpoint files remain unchanged. Final packaging commit is bound
in the generated distribution manifest after each published packaging change.

Official fastest-lap video and final source/video consistency remain pending.
All team members' IBM SkillsBuild course completion remains unverified; no completion
claim is made. No final release/tag until the video consistency gate is complete.
The official video uses stock track textures. The separate branded track copy and
editable artwork are [showcase material](../presentation/README.md), not new lap evidence.
