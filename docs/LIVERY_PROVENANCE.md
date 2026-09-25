# Livery identity investigation

The user-supplied [IBM SkillsBuild submission screenshot](../evidence/ibm-submission-requirements.png)
explicitly requires a publicly accessible repository containing AI car code and car
livery. Inclusion for this submission is established; no broader artwork license
is inferred. It also requires the fastest standing-start Corkscrew video, unchanged
submission livery and unchanged car-model dynamics. All team members must finish
“IBM Granite Models for Software Development”; completion needs participant confirmation.

Read-only inspection found two distinct image-bundled configurations:

| Configuration | scr_server index 0 / scr_server 1 | Livery SHA-256 |
|---|---|---|
| Qualified `/usr/local/torcs/share/games/torcs/drivers/scr_server` | car1-trb1 | `05bc6e7f24528cc66ca01358ec9ba78427b5ed413d7f5471c2e775bb2de0987c` |
| Separately bundled `/usr/local/share/games/torcs/drivers/scr_server` | car1-ow1 | `626bd81917353a81597a0400fd2758ee8901a7b3daa9b6b2afaa6bb710b8e231` |

The qualified harness explicitly uses the first installation as its data directory.
Race XML selects SCR index 0; its driver XML names scr_server 1 and car1-trb1.
The graphics binary contains driver/index texture search paths before the car
fallback. The packaged RGB matches the first installation and all ten of its SCR
copies. It also matches the stock berniw/3 skin; a filename alone is not provenance.

Container image: `docker.io/johnsloe/torcs-competition:amd64`, immutable registry digest
`sha256:16681a45956067f2afaae579bac3373e02c93848168c4c494777a8ffa1196b68`.
Container diff reports no changes under either installation; neither is a mounted
volume. Thus the files predate this container's engineering work. Image history
specifically copies `scr_server.zip` and extracts it to the second installation.
That archive is removed during image build. This makes the alternate configuration
material evidence, not an arbitrary unrelated filename.

The read-only baseline has no RGB/starter archive, and selects SCR index 0 without
identifying its model. No personal `.torcs` RGB override was found. The image name
and immutability do not independently prove organizer intent between the two roots.
[Raw trace](../evidence/livery-trace/trace.json) and both driver XMLs preserve the findings.
No asset, baseline, simulator configuration or RC1 source was changed; no race ran.

## Resolved by IBM competition documentation

Established by IBM competition documentation: the scr_server student workflow uses
the car1-trb1 driver livery; car1-trb1.rgb is driver slot 1 (default). The
[driver override instructions](../evidence/ibm-customising-driver-override.png)
identify drivers/scr_server/0/car1-trb1.rgb as loaded first during a race.
The [default-slot instructions](../evidence/ibm-customising-default-slot.png),
[texture overview](../evidence/ibm-customising-textures.png) and
[student setup excerpt](../evidence/ibm-student-setup.png) preserve the supplied evidence.

Established by IBM submission instructions: a car livery must be included in the
public GitHub repository and the official submission livery must not be changed.
No broader copyright or artwork license is inferred.

Together with the recorded XML mapping and byte comparison, this establishes the
packaged RC1 car1-trb1.rgb as the competition livery for scr_server 1. SHA-256 remains
05bc6e7f24528cc66ca01358ec9ba78427b5ed413d7f5471c2e775bb2de0987c.
The guide's installation prefix differs; the relative driver override and car
identity agree. The car1-ow1 archive is an alternate bundled configuration and no
longer blocks release. No livery, controller, parameters, physics or race configuration
were changed.
