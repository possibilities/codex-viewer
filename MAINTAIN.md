# Codex Viewer fork maintenance

This is the workshop for the standalone Codex conversation viewer. It owns
the viewer's required behavior, maintenance gate, launcher, and exact consumer
pin. [SCRATCHPAD.md](SCRATCHPAD.md) records observed state and unresolved
delivery work; it does not redefine this contract.

Invoke **`/maintain` with no arguments from this repository**. The shared
skill selects this contract's merge-only procedure automatically; no project
name or branch-policy reminder is required.

## Purpose

Keep a standalone, chromeless, read-only viewer built from Codex's native
conversation cells. A session UUID opens saved or ongoing Codex conversation
history. An explicit AgentVoice JSONL path opens observed voice text. Neither
mode submits a model turn or changes the conversation it displays.

The outer repository owns the launcher and fork workflow. The inner fork owns
rendering, session reads, and the voice reader. Retaining unused Codex code is
acceptable; extracting a second renderer or shrinking Codex's dependencies is
not a goal. Preserve the behavior below through upstream changes.

## Upstream

- Bound checkout: `codex/`, the submodule in this workshop. `upstream` is
  `https://github.com/openai/codex.git`; upstream's branch is `main`.
  `origin` is `possibilities/codex` (HTTPS or GitHub SSH transport).
- Read the complete applicable `codex/AGENTS.md` hierarchy before editing the
  fork, plus [CONTEXT.md](CONTEXT.md) and the [ADRs](docs/adr/README.md).
- The public fork repository is shared with other work, including codpiece.
  This workshop owns only `refs/heads/codex-viewer`. It does not own `main`,
  `integration`, `carry/*`, upstream offer heads, or historical branches.
- Stance: maintain the viewer downstream. No upstream contribution is part of
  a maintenance cycle. A generally useful defect fix can be considered as a
  separate, explicitly authorized contribution after reading current upstream
  contribution guidance. Do not send issues, requests, or comments in passing.
- A carry is replaceable only when the captured upstream code satisfies its
  whole behavioral contract, confirmed by reading and exercising it. An
  upstream read-only resume screen, merged request, or similar class name is
  evidence, not proof that a standalone viewer is redundant.

## Branch model

- Consumer branch: `codex-viewer`, the workshop's integration role under its
  established public name. The outer `codex/` gitlink selects an exact commit
  reachable from this published branch. `.gitmodules` names the same branch;
  cloning or installing must not float to its newest tip.
- Composition: **merge-only maintained history**, with upstream merges and
  behavior repairs committed forward. Never rebase or force-push the public
  branch. Retiring a carry removes redundant code in a new commit rather than
  deleting published commits. There are no separate viewer carry heads.
- Mirror branch: **none owned by this workshop**. `upstream/main` is a fetched
  upstream reference, not a publication target. The old local `main` in the
  submodule is historical state; do not turn it into a mirror in passing.
- This selects the shared maintain skill's merge-only procedure rather than
  its rebased integration and mirror transaction. Follow its capture, semantic
  audit, gate, and state-reporting discipline, but use the merge and single-branch
  publication procedure below. **Do not invoke its shared namespace script**:
  it can rewrite history and move refs this workshop does not own. See
  [ADR 0002](docs/adr/0002-maintain-the-viewer-as-a-workshop.md).
- `scripts/reconcile-branches.sh --check` checks the committed outer pin
  against the actual published viewer head. `--pin SHA` checks a prospective
  pin. It reads refs and objects without fetching or modifying them. A missing
  remote-tip object needs an explicit fork fetch before retrying. `--apply`
  is intentionally unsupported; there is no automatic branch repair.
- `--print-model`, `--configure-supervision`, and `--check-supervision` expose
  the same ownership to local advisory tools. The derived configuration names
  `codex-viewer` as trunk, no mirror or carry namespace, and this workshop's
  nested checkout. It does not change any branch or remote.
- Deletion marker prefix: `DELETEME/`. Creating, moving, or deleting a marker
  or any undeclared ref needs an explicit human decision naming that ref.
  Open upstream request heads are preserved, not maintained or exact-head
  validated here. Rerere is not relied on; reread any reused resolution.

### One maintenance cycle

1. Start with clean outer and inner trees and inventory both repositories'
   worktrees. A fresh clone may have the submodule detached for consumption;
   switch it to `codex-viewer` before editing. Preserve pre-existing local
   commits and reconcile unpublished work deliberately, never by resetting.
2. Capture all fork heads, the exact published viewer head, and one upstream
   `main` SHA in cycle-owned working notes **before fetching**. Fetch that
   upstream object once (`git -C codex fetch --no-tags upstream "$upstream_sha"`)
   and the viewer branch separately. Keep that upstream target fixed for the
   entire cycle. Do not chase a moving upstream branch during validation.
3. Read every upstream commit since the separately recorded audited frontier
   and assign every feature below a keep, repair, or retire disposition.
   The delivered upstream base is not proof of a completed audit. If no audit
   frontier is known, establish and record an explicit first-audit range from
   the original fork base; do not invent a historical successful audit.
4. Work on an owned, named candidate branch/worktree descended from the viewer
   tip. Merge the captured upstream SHA and commit the repairs. Never edit a
   detached submodule HEAD. Keep the bound checkout and installed launcher
   intact while preparing the candidate.
5. Run the Gate below on the exact committed candidate. Fix failures and
   commit changes before producing final evidence. Read every snapshot change;
   do not accept upstream drift as a new expectation without review.
6. When publication is authorized, prove the captured public viewer head is
   still current and is an ancestor of the candidate. Push only the candidate:
   `git -C "$candidate_worktree" push origin "$candidate_sha:refs/heads/codex-viewer"`.
   This is an ordinary fast-forward push, without a force option. A moved head
   or rejected push ends publication; inspect the race rather than retrying
   against newly captured state. Re-read the published head before handover.
7. Run Consumer, then the pin and supervision checks. Update the scratchpad
   with actual gate, publication, pin, and installation outcomes. Advance the
   audited frontier only after the whole interval and inventory were reviewed.
   Commit the outer pin and state together; publish them only after the inner
   commit is fetchable. Remove only clean worktrees created by this cycle.

A request to scaffold or document this workshop is not a completed maintenance
cycle or standing permission to publish unrelated work. A future maintenance
request includes the declared viewer update and consumer handover, subject to
any narrower instruction in that session.

## Features

Every product change updates this inventory and its verification mapping in
the same unit of work. These are behavior groups in the merge history, not
new branch names. Source paths below are relative to `codex/codex-rs/`.

| ID | Required behavior and scope | Evidence to retain |
| --- | --- | --- |
| V1 | Standalone `codex-viewer` binary in `codex-tui`; one session UUID or `--voice-jsonl FILE`, mutually exclusive. `--follow` is voice-only; native sessions follow automatically. Preserve `-c` and `--no-alt-screen`. No composer, harness controls, or turn submission. Scope: `tui/src/bin/session-viewer.rs`, `cli.rs`, `lib.rs`, `startup_draft.rs`, `startup_orchestration.rs`, `session_viewer.rs`. | Binary CLI tests and `renders_only_the_conversation`, `renders_stable_loading_surface`; terminal smoke. |
| V2 | Render native user, assistant Markdown, reasoning under display policy, command, tool, and file-change cells. Preserve native diff background styling across the pane and workspace link context. Scope: `session_viewer/transcript.rs`, `viewport.rs`, `thread_transcript.rs`, pager helpers. | `renders_native_markdown_command_and_file_change_cells`, `diff_line_backgrounds_fill_the_viewer_width`, and reviewed snapshots. |
| V3 | Show the recent conversation promptly with stable loading while older history is prepared off the input loop. Bound the initial active-turn tail; backfill without dropping or duplicating newer entries. Read only complete local rollout records and avoid rereading unchanged files. Local follow polls at 100 ms. Scope: `session_viewer/rollout_watcher.rs`, `viewer_state.rs`, `session_viewer.rs`. | Rollout watcher tests, including bounded initial tail, split/appended records, and latest-turn replacement; long-history smoke. |
| V4 | Reader controls the viewport. Tail follows new content; scrolling away preserves position until returning to the end. Retain cached layout for unchanged cells, keyboard/page/Home/End navigation, mouse wheel, resizing, Ctrl-C exit, and terminal restoration. Scope: viewport, viewer state, pager helpers, TUI event stream and cleanup. | Follow/layout tests, `vertical_mouse_scroll_maps_to_arrow_keys`, terminal smoke while appending and resizing. |
| V5 | When a local rollout is unavailable, native app-server reads provide the latest full turn, including in-progress assistant deltas, without resuming the thread or starting a turn. Poll at 250 ms while following; merge replacements without duplicates. Scope: `app-server/src/thread_state.rs`, `request_processors/thread_processor.rs`, `tui/src/app_server_session/history.rs`. | `turns_list_includes_streaming_assistant_text_in_latest_page` exercises the public RPC, active-turn text, full items, and pagination. |
| V6 | Explicit AgentVoice file reader bypasses app-server and native session lookup, reusing native user/assistant cells and normal display config. Accept the documented `voice_transcript` header and v2 event envelopes; isolate items by producer, generation, conversation, and item ID. Completion replaces drafts; unknown-speaker deltas wait; interruptions mark unfinished text incomplete. Scope: `session_viewer/voice_transcript.rs`, `voice_viewer.rs`. | Voice reducer, CLI, and snapshot tests; saved and growing file smoke. |
| V7 | Voice pane has no header/footer or recording notices. Center “Waiting for voice messages…” until user or assistant text exists. Ctrl-C closes only the viewer; q/Ctrl-Q do not close voice viewing. Follow complete records at 100 ms; reject malformed input, truncation, replacement, identity changes, and over-budget input (1 MiB/record, 256 KiB/message, 64 MiB total text, 100,000 entries). Scope: voice reader/viewer and their tests. | Empty/first-message snapshots, split UTF-8, replacement/truncation, identity and size tests; terminal smoke. |
| V8 | Keep the small non-product adaptations needed to validate this fork visible: debug/release command-popup snapshot selection, precise pet payload assertion, current update-prompt snapshot, and deterministic exploring-indicator snapshot. Scope: `tui/src/bottom_pane/command_popup.rs`, `pets/mod.rs`, `chatwidget/tests/exec_flow.rs`, corresponding snapshots. | Full `codex-tui` suite; inspect these against upstream each cycle and remove in forward commits when equivalent fixes arrive. |

V1–V7 retire only when upstream supplies their complete behavior at this
standalone viewer boundary. V8 adaptations retire individually when unnecessary.
The voice format is observed text, not an audio playback or delivery guarantee;
its detailed public format and limits remain in [README.md](README.md).

## Gate

For workshop-only changes, run from the outer repository:

```sh
./tests/validate.sh
./bin/codex-viewer --help
```

For a fork candidate, run from its named, clean worktree, substituting the
absolute workshop path if this checkout lives elsewhere:

```sh
/Users/arthack/code/codex-viewer/scripts/gate.sh --worktree "$PWD"
```

The gate first builds runtime helper binaries from `codex-cli`,
`codex-code-mode-host`, `codex-rmcp-client`, `codex-exec-server`,
`codex-shell-escalation`, and `codex-exec` in the isolated target. Tests run
without inherited `NO_COLOR` or personal/system Git configuration so ANSI
assertions and committed project-config fixtures are reproducible.
It then runs `just test -p codex-tui -p codex-app-server`, then
`just fix -p codex-tui -p codex-app-server`, then `just fmt`. It fails if fixes
or formatting change the committed candidate; it does not rerun tests after
those commands. It builds release through this workshop's `scripts/setup.sh`
in a temporary launcher layout and checks the freshly built binary's help.
It never selects that candidate in the installed launcher's `.build` directory.
The receipt names the candidate commit/tree and binary digest. It proves the
automated gate only. Start with two Cargo jobs; keep the large target cache on
Scratch when mounted. Never run concurrent native gates against one target.

If repairs touch other crates, run their required checks too, following inner
guidance. Do not expand to the full Codex workspace suite without the approval
that guidance requires. Release-only fixture edits also need the corresponding
release tests. New visible behavior requires reviewed native snapshots.

Before publishing, exercise the fresh candidate in a real terminal: a saved
native session with Markdown, commands and diffs; a long growing conversation
while scrolled away and after returning to the tail; resize and Ctrl-C with no
terminal debris; an empty voice file followed by text, completion and an
interruption; and saved voice viewing without `--follow`. Check alternate and
`--no-alt-screen` modes. Use owned sessions and synthetic recording fixtures;
do not commit personal transcripts. Record what was actually exercised and
any coverage gaps. Hosted CI is not currently a publication requirement.

## Consumer

This workshop's committed gitlink and launcher are the consumer binding.
AgentVoice also invokes `codex-viewer --voice-jsonl FILE --follow` from PATH
for `agentvoice attach voice`; its viewer lifetime is independent of recording
and voice. Keep that CLI contract stable. No other workshop's pin moves here.

After the candidate is gated and its inner commit published, from the clean
outer checkout on `main`, with `codex/` clean on `codex-viewer`:

```sh
./scripts/update-pin.sh --sha "$candidate_sha"
git add codex SCRATCHPAD.md
git commit -m "chore: update maintained Codex viewer"
```

The consumer command verifies published reachability, fast-forwards the bound
viewer checkout, builds through setup, and checks help. It leaves the gitlink
change for review with the scratchpad; it neither commits nor pushes. A failed
build leaves the previous committed outer pin intact and reports failure.
Review any changed inner checkout before continuing. Publish the outer commit
only after the inner commit; then run `./scripts/install.sh` when installation
is part of the cycle and check the installed command. No active application
restart is required.

Fresh consumers use `git submodule update --init` and `./scripts/install.sh`
to build the committed pin. `CODEX_VIEWER_PROFILE=debug` is only for local
development. An existing `.build` symlink or successful `--help` alone does not
establish which source revision produced an old binary.

## Notify

- Title: `Codex Viewer Maintenance`
- Group: `codex-viewer.maintain`

Report outcome, upstream reviewed, feature dispositions, gate evidence,
published viewer commit, outer pin, and installation separately. A failed
publication check or unfinished audit stays visible in the scratchpad.

## Hosted gate trial

The 2026-09-09 request authorizes publishing CI candidates separately from the
consumer branch. Both repositories are public. A candidate may be pushed,
without force, to a new `viewer-ci/<cycle>-<short-sha>` branch in
`possibilities/codex`; preserve existing refs. This is validation publication,
not consumer promotion. Push the candidate first so the existing outer pin's
objects are fetchable, then publish the workshop workflow to outer `main`.

Dispatch the workshop's `native-gate.yml` with the exact full `candidate_sha`:

```sh
gh workflow run native-gate.yml --repo possibilities/codex-viewer \
  -f candidate_sha="$candidate_sha"
```

The trial uses a macOS 15 runner with full Xcode, builds the pinned V8 from
source, and executes `scripts/gate.sh` unchanged. It reduces debug information
and disables incremental compilation to conserve runner disk. Logs, candidate
diff/status, and run identities are retained on failure; a successful run also
uploads the release binary and gate receipt. Record the run URL and actual
outcome in the scratchpad. A queued or running job is not a successful gate.

Only a successful exact-candidate run can substitute for the local automated
gate. Verify its receipt, workflow revision and binary digest; local terminal
smoke remains required before consumer promotion. Keep the original upstream
snapshot and public consumer-head check for the maintenance cycle. Do not move
the consumer branch or install an artifact just because CI was dispatched.
This route remains a trial until a full run succeeds.
