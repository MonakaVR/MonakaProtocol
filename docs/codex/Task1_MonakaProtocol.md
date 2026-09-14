# Codex Task 1 bootstrap

The full Task 1 specification is intentionally maintained on the work branch only, so that the task document has a single authoritative copy during implementation.

## Start procedure

1. Read the repository-root `AGENTS.md`.
2. Run `git fetch --no-prune origin`.
3. Confirm that remote branch `origin/refactor/monaka-layer-separation` exists.
4. Switch to that existing branch without recreating, rebasing, resetting, or rewriting it:
   `git switch --track origin/refactor/monaka-layer-separation`
   If the local branch already exists, switch to it instead.
5. After switching branches, read **this same path again**:
   `docs/codex/Task1_MonakaProtocol.md`
6. The file on `refactor/monaka-layer-separation` is the complete Task 1 implementation specification. Follow its constraints, procedure, Definition of Done, and final-report format.

Do not implement Task 1 from this bootstrap file alone. Do not modify `main` as part of Task 1 implementation.
