# MonakaProtocol repository instructions

This repository owns the MonakaVR shared protocol contract: data models, schemas, codecs, validation, fixtures, version compatibility, and distributable protocol kits.

## Current coordinated Architecture Revision

On `refactor/monaka-layer-separation` at and after commit `572e58cfa20b8b4335207ea5dbcb3f04c587ddff`, the current coordinated Architecture Revision supersedes the older fixed-v1 Task 1 instructions wherever they conflict.

Read repository-local normative material in this order before making implementation changes:

1. `docs/architecture-revision.md` — current Architecture Revision and migration intent.
2. `docs/C2.md` — current wire 2.0 contract.
3. `docs/C1.md` — inherited rules only where C2 explicitly says they remain unchanged; otherwise historical wire 1.0 contract.
4. `docs/codex/Task1_MonakaProtocol.md` — historical Task 1 baseline and v1 evidence, not authority to revert the coordinated v2 revision.

Do not remove or rewrite the v1 implementation/artifacts merely because v2 is current. v1 remains historical compatibility/evidence. Conversely, do not revert v2 fields, identity semantics, modality semantics, or validation merely to satisfy an older Task 1 paragraph.

If a future user instruction explicitly replaces this revision, record the new precedence rather than silently reconciling contradictory specifications.

## Repository-wide constraints

- Work only in this repository unless the active coordinated task explicitly states otherwise.
- Do not add PICO/VIVE device access, runtime socket services, mapping/calibration, GUI, body-role assignment, Fusion/Fallback/IK, or SteamVR driver responsibilities to MonakaProtocol.
- Do not invent or silently change wire fields, units, coordinate conventions, version semantics, ports, or public API names defined by the active contract.
- Preserve unrelated existing work and uncommitted changes.
- Do not delete branches, force-push, rebase, amend, or otherwise rewrite history.
- Keep implementation commits small and reviewable.
- Run the applicable build and tests before reporting a task complete. Explicitly report anything that could not be verified.
- Do not claim hardware validation when no hardware validation was performed.
- A downstream v2 migration may consume only an actually generated, hash-pinned v2 kit from a clean committed source tree. Do not fabricate artifact hashes or treat source files alone as a fixed handoff.

If repository state conflicts with the active Architecture Revision or C2, inspect the difference and report it rather than overwriting or discarding work.
