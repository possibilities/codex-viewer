# Codex Viewer context

**Workshop** — This repository owns the viewer fork's behavioral contract,
maintenance gate, launcher and consumer pin. `MAINTAIN.md` specifies required
behavior; `SCRATCHPAD.md` records current delivery and audit evidence.
_Avoid_: second renderer, Codex mirror.

**Launcher** — This repository's `codex-viewer` entrypoint, which selects the
tested native viewer build. The implementation belongs to the maintained Codex
fork rather than a second transcript renderer here.
_Avoid_: app-server, harness.

**Viewer fork** — The public `codex-viewer` branch of `possibilities/codex`,
updated without rewriting published history and pinned through `codex/`.
It fills the workshop integration role; the shared fork's literal `integration`
branch is outside this workshop.
_Avoid_: detached patch, rebased integration stack.

**Audited-upstream frontier** — The exact upstream commit through which a
complete maintenance review assigned every carried behavior a disposition.
An upstream merge, successful build, or newer outer pin does not advance it.
_Avoid_: merge base, latest tested upstream.

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
