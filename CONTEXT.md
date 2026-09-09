# Codex Viewer context

**Launcher** — This repository's `codex-viewer` entrypoint, which selects the
tested native viewer build. The implementation belongs to the maintained Codex
fork rather than a second transcript renderer here.
_Avoid_: app-server, harness.

**Viewer fork** — The public `codex-viewer` branch of `possibilities/codex`,
updated without rewriting published history. The outer repository binds an exact
commit through the `codex/` submodule.
_Avoid_: detached patch, integration branch.

**Outer pin** — The committed submodule revision selecting the native viewer
implementation for consumers. Its corresponding inner commit must be published
before the outer pin is pushed.
_Avoid_: latest Codex, automatic upgrade.

**Native session** — A Codex conversation selected by its session UUID and read
through native session storage or the supported app-server read path. Viewing
does not create a composer or submit a model turn.
_Avoid_: recording, synthetic session.

**Voice recording** — An AgentVoice JSONL file read with `--voice-jsonl`, separate
from Codex history. Its observed text events and interruption markers describe
what was recorded, not proof of completed audio playback or complete delivery.
_Avoid_: Codex rollout, speech replay.

**Follow** — Keeping the viewport at newly available conversation content while
the reader is at the tail. Manual scrolling preserves the reader's position
until they return; follow does not change the conversation itself.
_Avoid_: resume, live agent attachment.
