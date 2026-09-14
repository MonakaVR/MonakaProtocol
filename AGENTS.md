# MonakaProtocol repository instructions

This repository owns the MonakaVR shared protocol contract: data models, schemas, codecs, validation, fixtures, version compatibility, and distributable protocol kits.

## Codex task entry point

For the current layer-separation work, read `docs/codex/Task1_MonakaProtocol.md` completely before making implementation changes. Treat that task document as the normative task specification for this work.

## Repository-wide constraints

- Work only in this repository unless the task specification explicitly states otherwise.
- Do not add PICO/VIVE device access, runtime socket services, mapping/calibration, GUI, body-role assignment, Fusion/Fallback/IK, or SteamVR driver responsibilities to MonakaProtocol.
- Do not invent or silently change wire fields, units, coordinate conventions, version semantics, ports, or public API names defined by the task specification.
- Preserve unrelated existing work and uncommitted changes.
- Do not delete branches, force-push, rebase, amend, or otherwise rewrite history.
- Keep implementation commits small and reviewable.
- Run the applicable build and tests before reporting a task complete. Explicitly report anything that could not be verified.
- Do not claim hardware validation when no hardware validation was performed.

If repository state conflicts with the task document, inspect the difference and report it rather than overwriting or discarding work.
