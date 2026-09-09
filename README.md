# codex-viewer

`codex-viewer` is a chromeless, read-only terminal viewer for saved and ongoing [Codex](https://github.com/openai/codex) sessions and explicit AgentVoice recordings. It renders the native Codex conversation cells without a composer or other harness chrome, follows new conversation entries in real time, and keeps manual scroll position until you return to the tail.

This repository is the workshop for the viewer fork: it owns the top-level
`codex-viewer` command, an exact `codex/` submodule pin, and the behavior and
checks required to maintain it. The implementation lives on the public
[`codex-viewer`](https://github.com/possibilities/codex/tree/codex-viewer)
branch. [MAINTAIN.md](MAINTAIN.md) is the maintenance contract;
[SCRATCHPAD.md](SCRATCHPAD.md) records the current baseline and delivery gaps.

## Install from source

Requirements are the same as a source build of Codex: Git, a current Rust toolchain, and the native build tools required by the Codex workspace.

```bash
git clone --recurse-submodules https://github.com/possibilities/codex-viewer.git
cd codex-viewer
./scripts/install.sh
```

The installer builds an optimized viewer and links `codex-viewer` into `${PREFIX:-$HOME/.local}/bin`. Make sure that directory is on `PATH`.

For a repository-local build without installing a command:

```bash
./scripts/setup.sh
./bin/codex-viewer --help
```

## Use

Pass a Codex session UUID:

```bash
codex-viewer 01a0182c-1cde-7282-ad47-84394206032e
```

Use Up/Down, Page Up/Page Down, and Home/End to move through the conversation. New entries remain pinned to the bottom while following; scrolling upward pauses following until you return to the end. Press Ctrl-C to exit.

The session-UUID path uses Codex's normal configuration and session storage. CLI configuration overrides are accepted with `-c key=value`.

## AgentVoice recordings

In the AgentVoice checkout, explicitly capture future voice events:

```bash
bun run voice:record --workspace ~/code/myapp --out-dir ~/voice-recordings/myapp
```

The recorder prints the file path. Open it in another terminal:

```bash
codex-viewer --voice-jsonl ~/voice-recordings/myapp/<thread-id>.jsonl --follow
# Saved viewing:
codex-viewer --voice-jsonl ~/voice-recordings/myapp/<thread-id>.jsonl
```

This is a local-file reader using native Codex user and assistant cells. It does
not start app-server, fetch Codex threads, or create fake Codex sessions. It reads
normal display configuration; the recorded workspace supplies link context.
`--voice-jsonl` and a session UUID are mutually exclusive. `--follow` is only for
voice files; native session viewing already follows automatically.

Draft text updates in place, and native completion replaces it with canonical
text. Whitespace is trimmed for display only. Items are isolated by controller
instance, runtime generation, conversation and item identity. Unknown-speaker
deltas wait for a canonical item. Recording interruptions mark partial messages
incomplete. The chat fills the pane without recording notices, a header, or a
footer. A file belongs to one conversation: Fresh creates a new file; redials
append. Open the new path after Fresh. Ctrl+C exits the viewer without stopping
voice or recording; q and Ctrl+Q do not close it.

An empty voice transcript shows a centered “Waiting for voice messages…” placeholder
until user or assistant text arrives. Empty items and unknown-speaker deltas keep
the placeholder visible.

The AgentVoice JSONL format has a `voice_transcript` header (`format: "agentvoice"`,
`workspace`, `threadId`), original `voice.item.*` event envelopes, and
`recording.started`, `recording.gap`, and `recording.ended` markers. Each record
carries observer `observedAt` time. The event envelopes use AgentVoice's current
contract (`v: 2`). No speech backfill or complete-delivery guarantee is implied;
these are observed text events, not evidence that audio playback finished.

The reader polls every 100 ms and displays only complete newline-terminated
records. Malformed records, truncation, or file replacement produce explicit
errors. Reopen after truncation/replacement.
Limits: 1 MiB per record, 256 KiB per message, 64 MiB total text and 100,000 entries.
Recordings are independent of Codex history and are never sent to a model.

## Development build

The setup script builds release mode by default. A faster development build can reuse any absolute Cargo target directory:

```bash
CARGO_BUILD_JOBS=2 \
CODEX_VIEWER_PROFILE=debug \
CODEX_VIEWER_TARGET_DIR=/path/to/shared/codex-target \
./scripts/setup.sh
```

The launcher follows `.build/codex-viewer`, so it continues to use the exact binary selected by the last successful setup.

## Updating Codex

Follow [MAINTAIN.md](MAINTAIN.md) for the feature inventory, upstream audit,
candidate gate, and consumer handover. The viewer branch keeps its published
history through upstream merges. This workshop shares `possibilities/codex`
with other projects and owns only its `codex-viewer` branch.

Add upstream once if it is absent, then configure workshop discovery:

```bash
git -C codex remote add upstream https://github.com/openai/codex.git
./scripts/reconcile-branches.sh --configure-supervision
./scripts/reconcile-branches.sh --check-supervision
```

Inspect the model or verify that the committed pin is publicly fetchable:

```bash
./scripts/reconcile-branches.sh --print-model
./scripts/reconcile-branches.sh --check
```

The checker is read-only and needs Python 3 and Git. It never fetches, resets,
renames, or pushes branches. A missing published-tip object requires fetching
`origin codex-viewer` before retrying. An unpublished pin must be resolved
before publishing an outer update. Consumers do not advance until the exact
inner commit is published and the outer pointer is reviewed and committed.

## Live-update boundary

For local sessions, the viewer follows complete rollout records at 100 ms intervals. When the rollout is not locally readable, it polls the app-server's latest full turn at 250 ms intervals; active assistant text includes accumulated delta events.
