# AGENTS.md — how to work in this repo

## The loop (every task)
1. **Read `memory.md` first.** Do not re-scan the repo.
2. Do the task.
3. **Update `memory.md` last** — what changed, decisions, next step. Summarize aggressively.

## Non-negotiables
- **The app role must never gain SELECT on `RAW_CASES`, `PARSED`, or `EXTRACTED`.**
  That grant boundary is the entire thesis. If a task seems to need it, the task is wrong.
- **Never commit real secrets.** `.env` is git-ignored; `.env.example` is the template.
- **Never use real casework data.** Synthetic only, and labelled as such.
- **Do not claim compliance.** Redaction is "a first pass that makes human review
  tractable", never "GDPR/HIPAA compliant".
- **Do not fake a capability verdict.** If a Cortex function failed the gate, ship the
  fallback and say so.

## Build order
Legs are additive and committed separately so the build can stop anywhere and still ship:
`00_gate` -> `10_leg_a` -> `20_leg_b` -> `30_leg_c`. Never start a later leg before the
gate verdict for it is recorded in `memory.md`.

## Cut list (do not build)
Auth, accounts, charts, extra file types, dark mode, a landing page, migrations, tests
beyond one smoke test.

## Commits
Conventional Commits. `feat:`, `fix:`, `docs:`, `chore:`.
