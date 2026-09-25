# ATLAS presentation package

HUMAN LED AI ACCELERATED RACE PROVEN

Official video: exact RC1, original track textures, normal qualified GUI setup.
Showcase: explicitly separate engineering presentation; not official race evidence.
See RULES_MATRIX.md for the supplied IBM documentation boundary.

## Track artwork

Inspection found banner references in `corkscrew.acc`, not advertising entries in
the track XML. XML textures describe surfaces and are untouched. `corkscrew_arbor.png`
is a complete track-name board; `kilo.png` is complete sponsor artwork. Both are
independently referenced by the model. Structural atlases (`64PASS*`, `dekk02`) and
braking markers are deliberately excluded. Existing UV mapping, geometry, surfaces,
collision data, timing and racing line are unchanged.

The isolated `showcase-track/` copy differs only in those two PNGs. It is not wired
into the simulator or the official recording. No installed file differs from stock.
The manifest records all original track hashes, dimensions and target paths.

`artwork/` contains editable SVG and exact SGI RGB output, plus PNG previews. The
installed model references PNG; those filenames and dimensions must be retained.
SGI RGB exports are deliverables for a compatible texture binding, not files to
rename over PNGs. No model/scene edit is needed or authorized here.

Hero and engineering variants are assigned to the two identified textures.
Evidence and method variants are showcase cards/unassigned banner masters; do not
invent additional track texture replacements. The 512-pixel hero tagline is the
largest single-line fit. Readability in motion is not yet verified; no lap was run
for a screenshot. This remains a presentation review package, not approved footage.

Generate deterministically in the existing container:
`python3 presentation/build_presentation.py` (Pillow and DejaVu Sans Bold).
Restore the local showcase copy: `python presentation/restore_showcase.py`.
Neither command writes to the installed track or `checkpoints/RC1`.
Originals/full track copy stay local. Track attribution is recorded in the manifest.

## Curated evidence and video

Use existing path-and-delta and controls plots without regeneration. The two new
cards summarize preserved checkpoint facts: progression (with distinct evidence
levels) and qualification. All displayed measurements have recorded evidence.

Official title: **ATLAS RC1 | 84.388 s | Corkscrew Standing Start**.
Description: Frozen RC1, scr_server 1, unchanged competition livery and car dynamics.
Preserved timing and GUI qualification: 84.388 s, zero damage. Link the public repo.
Only describe new footage as matching this result after the video trace is checked.

Showcase storyboard (separate from official video):
1. ATLAS / HUMAN LED AI ACCELERATED RACE PROVEN.
2. 84.388 SECONDS / STANDING START / CORKSCREW / TIMING AND GUI QUALIFIED.
3. Existing path/delta and speed/throttle/brake plots, labelled recorded RC1 telemetry.
4. Progression card: distinguish audited history, reference and timing/GUI results.
5. Qualification card and repository link: inspect evidence, reproduce, challenge.

Do not fabricate telemetry, interpolate an overlay onto unmatched footage, or imply
the newly branded track was used for the historical qualified run. No video has yet
been captured. Final source/video consistency and course completion remain pending.

## Proposed future profile block — not applied

**ATLAS — autonomous engineering and validation**

HUMAN LED AI ACCELERATED RACE PROVEN

Directed an AI-assisted engineering process from controller experiments to a
reproducible 84.388-second Corkscrew standing-start lap. Built telemetry, rejected
timing-contaminated gains, and preserved matching timing and GUI qualification.
Explore the controller, failure analysis and evidence at EtherTabu/atlas-torcs-racing.

Use only after the competition submission is frozen. EtherTabu/EtherTabu is untouched.

## Public package scope

Original textures and the full showcase track are retained in the local laboratory,
not copied wholesale into Git. The build script can create them from the matching
installed track in the documented Linux environment. Restoration requires those
locally generated originals; it restores the copy, never the installed environment.
The two summary cards read the preserved benchmark/checkpoint values; existing
controls and path/delta plots are reused without alteration.
