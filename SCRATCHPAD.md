# Codex Viewer maintenance state

## Baseline — reconstructed 2026-09-08

This entry establishes the workshop from existing code and original
conversations. It is **not** a completed upstream maintenance cycle.

| State | Observed value |
| --- | --- |
| Outer baseline at reconstruction | `5b969170657f4cd09e2a71aeb1db1f91dafd6f10` |
| Committed outer pin / local viewer head | `d6ce3c6a703495d1abe00004074143880ffb79a8` |
| Published `origin/codex-viewer` (live ref read) | `924709511326890e9a12ef30e93e557077c37a06` |
| Upstream merged into that viewer history | `52e12e0cb506e7bb2c9e406fc84d922e274a0e40` |
| Upstream merge commit | `de3d1c4a024d4b6135984062f4fd930e14666d61` |
| Original fork base (parent of first viewer commit) | `956f590ad549e75913894614ce0cbec4d5fd677a` |
| Audited-upstream frontier | **Unknown. No complete historical audit established.** |
| Existing selected binary | `/Volumes/Scratch/codex-viewer-target/release/codex-viewer`; help runs, source identity not established by a build receipt |

The published viewer head is two commits behind the already committed outer
pin: `f39b1c1ee58651b335a14c50a1c93752c95159b9` makes voice viewing chromeless;
`d6ce3c6a703495d1abe00004074143880ffb79a8` adds the empty voice placeholder.
The publication checker correctly rejects the current outer pin. Preserve
these commits; gate and publish them before the next outer publication.
Do not rewrite the public branch or silently move the outer pin backward.

## Carried behavior evidence

All entries describe the local pinned viewer above. IDs map to the required
behavior and retirement conditions in [MAINTAIN.md](MAINTAIN.md#features).
Tests named there were inspected during reconstruction, not rerun as a native
suite. No feature is claimed to have been semantically audited against current
upstream in this entry.

| Feature | Introduction and subsequent evidence | Current disposition |
| --- | --- | --- |
| V1 Standalone read-only entry | `cfbb2fd2a9` introduced the viewer; `fc8d8e4a37` named the binary; `b5a1443065` adapted startup to newer upstream. CLI tests exist separately from the library's `session_viewer` tests. | Retain; first full audit pending. |
| V2 Native rendering | `cfbb2fd2a9`; native-cell and diff-background snapshots plus transcript adapters at the current pin. | Retain; first full audit pending. |
| V3 Responsive local history | `1522b31253` split preparation from input handling and added recent-tail loading, background backfill, and cached layout tests. | Retain; first full audit pending. |
| V4 Viewport and teardown | `cfbb2fd2a9`, `1522b31253`; follow/layout/mouse tests and explicit terminal cleanup. | Retain; real-terminal gate remains required. |
| V5 Live app-server turns | `cfbb2fd2a9`, fixture adaptation in `b5a1443065`; public-RPC integration test for streaming text in the latest full turn. | Retain; first full audit pending. |
| V6 Voice file reader | `9247095113`; source, reducer tests, CLI validation and native voice-cell snapshot. | Retain; first full audit pending. |
| V7 Voice presentation and file integrity | `9247095113`, `f39b1c1ee5`, `d6ce3c6a70`; empty/first-message snapshots and malformed/replaced/truncated/oversized input tests. | Retain; last two commits not yet on published viewer branch. |
| V8 Validation adaptations | `b5a1443065`; release popup fixture, pet payload assertion, update-prompt snapshot. | Review each against upstream at first audit; do not treat as viewer features to preserve forever. |

## Provenance

Original conversations were found in the local Codex session archive; no
external-volume transcript recovery was needed. These are evidence locators,
not runtime dependencies or instructions to resume old sessions. The original
records are intentionally not copied into this public repository.

- Under `~/.codex/sessions/2026/08/18/`, file
  `rollout-2026-08-18T23-58-59-9e283d84-f52e-44d8-ae0e-7d290b59db37.jsonl`:
  line 9 requests conversation-only live viewing by session ID; 694–739
  establish standalone fork scope and allow retained unused code; 4904 and
  5059 require iterative scrolling/exit fixes while preserving the native
  approach; 6726 calls out diff styling; 7400 requests the pi-viewer-shaped
  outer repository; 9010–9069 call out slow load and scrolling stalls;
  11281–11326 establish the public fork branch and matching repository layout.
- Under `~/.codex/sessions/2026/09/06/`, file
  `rollout-2026-09-06T07-48-08-01a0768c-1c20-7c60-bece-d919da2dc6ed.jsonl`:
  1257 requests live and saved voice viewing through recorded text;
  1366 authorizes that implementation. The resulting code is `9247095113`.
- Durable implementation history: [first viewer](https://github.com/possibilities/codex/commit/cfbb2fd2a90ec855497cb06f4b8909eb2f85e4a2),
  [responsiveness work](https://github.com/possibilities/codex/commit/1522b312539d43d7ebb36e41dcc58c508001d6a5),
  [voice reader](https://github.com/possibilities/codex/commit/924709511326890e9a12ef30e93e557077c37a06).
- Workshop conventions were compared with local `zmax`, `tuilet`, `herdx`,
  `codpiece`, and `nekomancer` maintenance contracts and the shared maintain
  procedure. The merge-only/shared-fork exception is recorded in
  [ADR 0002](docs/adr/0002-maintain-the-viewer-as-a-workshop.md).

## Verification and next cycle

- Workshop shell syntax and 12 isolated Git/build-control tests pass. They use
  real disposable Git graphs and mocked Rust commands; they prove script
  boundaries, not native rendering or a release build.
- Existing `./bin/codex-viewer --help` passes. No Rust source, inner commit,
  outer pin, installed binary, or remote branch was changed by reconstruction.
- `scripts/reconcile-branches.sh --check` fails as expected on the unpublished
  pin above. This remains a delivery issue, not a waived check.
- Local supervision was configured and `--check-supervision` passes. Only
  derived `supervisor.*` Git configuration changed; no refs were moved.
- The first full cycle must gate the candidate and perform terminal smoke,
  resolve the publication gap, audit from the original fork base through its
  captured upstream target, and record an actual audited frontier. Native
  rendering, startup and history APIs have changed upstream; a clean merge
  alone cannot retire a carry.

## History

- **2026-09-08 — workshop reconstruction.** Established the behavioral
  contract, provenance, merge-only ownership exception, isolated native gate,
  publication checker, supervision declaration, and consumer update command.
  No upstream interval audited; no publication or installation performed.
