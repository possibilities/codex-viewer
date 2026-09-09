# 0002: Maintain the viewer as a workshop

Status: accepted, recorded 2026-09-08.

Codex Viewer owns a workshop contract, a behavioral inventory, an executable
gate, and a scratchpad separating delivered state from audited upstream state.
This makes the reasons for carrying code recoverable without replaying the
original development conversations. [ADR 0001](0001-pin-the-native-conversation-renderer.md)
continues to govern the renderer and outer/inner boundary.

The workshop preserves the public `possibilities/codex:codex-viewer` branch
with upstream merges and forward repairs. It does not adopt a rebased
`integration` branch or claim the fork's `main`: the existing repository
contract forbids rewriting the public viewer history, and codpiece uses the
same fork repository for a different product. This is an explicit exception
to the usual workshop branch model, not an incomplete rename. No user-facing
CLI or consumer pin changes merely because the workflow gains a name.

The cost is retaining merge history and maintaining a small local branch
checker instead of using the shared rewrite/mirror script. Feature retirement
must remove code forward, and each cycle must audit upstream semantically;
clean merges cannot establish parity. A future migration to a separate fork
or branch model needs its own decision and consumer transition.

The history reconstruction is evidence-based and retrospective. It does not
claim that old work passed today's gate or that an upstream merge was a full
maintenance audit. Current evidence and gaps live in
[SCRATCHPAD.md](../../SCRATCHPAD.md); the procedure and required behavior live
in [MAINTAIN.md](../../MAINTAIN.md).
