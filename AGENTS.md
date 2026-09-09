# Development Rules

Read [CONTEXT.md](CONTEXT.md) for launcher, native session and recording terms,
and [ADR 0001](docs/adr/0001-pin-the-native-conversation-renderer.md) before
changing the fork or viewer boundary.

- Keep this repository focused on the top-level `codex-viewer` launcher and maintained-fork workflow.
- `codex/` is a submodule of `possibilities/codex`, pinned to its public `codex-viewer` branch.
- Read and follow `codex/AGENTS.md` before changing code inside the submodule.
- Never edit Codex from a detached submodule HEAD. Switch to `codex-viewer`, merge `upstream/main`, validate the affected crates, and commit the inner fork before updating the outer pointer.
- Before publishing an outer pointer, push the corresponding inner commit to `origin/codex-viewer` so fresh clones can fetch it.
- Do not rebase or force-push the public `codex-viewer` branch.
- Build through `./scripts/setup.sh`; set `CODEX_VIEWER_PROFILE=debug` only for local development builds.
- After launcher changes, run `./bin/codex-viewer --help`.
