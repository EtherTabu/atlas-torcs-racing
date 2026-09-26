# Submission readiness

This checklist combines the authoritative IBM SkillsBuild submission screenshot
with demonstrated engineering evidence. See [requirement and livery evidence](LIVERY_PROVENANCE.md). The exact
official deadline, required video format and final upload procedure are not in
the available evidence and require human confirmation against the official rules.

| Check | Current evidence / remaining action |
|---|---|
| Public GitHub repository | **Complete.** Public repository: `EtherTabu/atlas-torcs-racing`, separate from the profile repository `EtherTabu/EtherTabu`. |
| AI controller code included | Present; selected runtime source hashes must match generated manifest. |
| Required car livery included | `assets/livery/car1-trb1.rgb` copied byte-for-byte from SCR driver index 0. Provenance and hash included. |
| Official livery unchanged | Local identity verified against qualification hashes. Public inclusion is explicitly required by IBM. Identity resolved by IBM Customising Guide: car1-trb1.rgb, default slot 1, SCR index 0; exact qualified bytes preserved. |
| Car dynamics unchanged | Qualification preserves installed car, track and physics hashes. No model dynamics are distributed as modified assets. |
| Corkscrew | Recorded race configuration and complete trace identify the selected track. |
| Standing start | First sensor: distRaced 0, speed effectively zero; official lap timer used. |
| Fastest qualified lap | Generated from the selected checkpoint; experimental Frontier laps cannot replace it without qualification. |
| Timing and GUI qualification | Preserved PASS report; nine identical timing repeats and matching normal GUI trace for RC1. Requalify changed driving/runtime artifacts or a new final candidate. |
| Official video | **PASS.** `ATLAS-RC1-submission-candidate.mp4`: complete standing start and genuine completion, unchanged 1x timing, full viewport/HUD, no added hold. Small noVNC handle and pointer retained. Preferred organizer-facing video, subject to organizer rules. |
| Source/video consistency | **PASS.** Completed [source/video record](SOURCE_VIDEO_CONSISTENCY.md) and `evidence/official_video.json` bind exact qualified trajectory, 84.388 s, zero damage and frozen identities. |
| Final commit/tag and manifest | Video consistency gate passed. Final tag `atlas-rc1-final` binds packaging; the generated release manifest records the actual final commit separately from capture-source commit `3427a92e8604fc14e88c99afb1d47ccb301f3a88`. See release assets for the generated manifest. |
| License and attribution | Existing source notices retained. Do not apply the code's MIT license to the livery or independently licensed simulator assets. IBM requires livery inclusion for this submission; no broader artwork license is asserted. |
| Official submission procedure | **Human confirmation required:** deadline, upload destination, video specification and any organizer rules not supplied here. |

Final organizer submission remains incomplete pending course completion confirmation,
organizer requirements confirmation and human upload.


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

Official fastest-lap video and source/video consistency are verified.
All team members' IBM SkillsBuild course completion remains unverified; no completion
claim is made. The video consistency gate is complete.
The official video uses stock track textures. The separate branded track copy and
editable artwork are [showcase material](../presentation/README.md), not new lap evidence.
