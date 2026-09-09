# 0001: Pin the native conversation renderer

Status: retrospective, recorded 2026-09-08 from the existing launcher and fork
contract. This records the current choice rather than asserting its original
decision date.

The viewer uses Codex's native conversation cells in the public maintained
`codex-viewer` fork. The outer repository owns a small launcher and an exact
submodule pin, while the inner fork owns rendering and native session reads.
This preserves native transcript behavior without independently reproducing it
in the launcher. A composer, model turn or session mutation is outside the
viewer contract.

The cost is a native build and an explicitly validated fork update. The public
branch is updated by merge without history rewriting, and the inner commit is
pushed before the outer pin so consumers can fetch exactly what was tested.
AgentVoice recordings use a separate local-file reader; they are not converted
into fake Codex sessions or sent to a model.

Evidence and current procedure: [README](../../README.md),
[repository rules](../../AGENTS.md), and [submodule declaration](../../.gitmodules).
