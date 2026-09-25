# Publication handoff

Target: **EtherTabu/atlas-torcs-racing**, public. Never modify EtherTabu/EtherTabu.
The existing local main history is the packaging history to push, not a new empty
copy. The public remote is live at https://github.com/EtherTabu/atlas-torcs-racing.
No final release/tag has been created; official video consistency remains pending.

Livery identity and required public inclusion are resolved by IBM documentation;
see [SUBMISSION_READINESS.md](SUBMISSION_READINESS.md). Preserve its exact bytes.

After resolution, use an existing authenticated GitHub session or Git credential
manager/API path; CLI installation is not intrinsically required. If authentication
is absent, request one GitHub sign-in/account action, never a token pasted into chat.
Create only the target repository, push reviewed main history, and verify public
README rendering, controller, livery, evidence, checklist and Actions workflow.
Confirm the CI run actually starts and inspect its result. Update the distribution
manifest with the actual repository and packaging commit only after they exist.
No final release/tag before video consistency review.
