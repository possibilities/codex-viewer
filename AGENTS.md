# Development Rules

Read [CONTEXT.md](CONTEXT.md) for workshop, launcher, native session and recording
terms, [MAINTAIN.md](MAINTAIN.md) for the fork contract, and the
[ADRs](docs/adr/README.md) before changing the fork or viewer boundary.
Read [SCRATCHPAD.md](SCRATCHPAD.md) for current state; never infer a completed
upstream audit or published pin from a successful old build.

- Keep this repository focused on the top-level `codex-viewer` launcher and maintained-fork workflow.
- `codex/` is a submodule of `possibilities/codex`, pinned to its public `codex-viewer` branch.
- Read and follow `codex/AGENTS.md` before changing code inside the submodule.
- Never edit Codex from a detached submodule HEAD. Switch to `codex-viewer`, merge `upstream/main`, validate the affected crates, and commit the inner fork before updating the outer pointer.
- Before publishing an outer pointer, push the corresponding inner commit to `origin/codex-viewer` so fresh clones can fetch it.
- Do not rebase or force-push the public `codex-viewer` branch.
- This workshop owns only `codex-viewer` on the shared Codex fork. Do not move
  `main`, `integration`, `carry/*`, or historical heads. Use the local
  `scripts/reconcile-branches.sh`, never the shared rewrite/mirror script.
- Maintain the behavioral inventory and its evidence when changing the fork.
  Keep delivered state separate from the audited-upstream frontier.
- Run `./tests/validate.sh` after workshop script changes. For inner changes,
  use the native gate and terminal checks in `MAINTAIN.md`.
- Build through `./scripts/setup.sh`; set `CODEX_VIEWER_PROFILE=debug` only for local development builds.
- After launcher changes, run `./bin/codex-viewer --help`.
