# CLAUDE.md — entry point for Claude Code in this repo

## Read order, every task
1. `memory.md` — durable project brain. Read first, update last.
2. `plan.md` — current roadmap and immediate next action.
3. `AGENTS.md` — the canonical engineering rules. **They are not repeated here.**
4. `03-PLAYBOOK-consent.md` — the product spec (PRD) for this build.

`AGENTS.md` is authoritative for conventions. This file only describes *how to operate*.

## What this project is
A Snowflake-native redaction pipeline. A charity's messy private casework file becomes
a publishable impact brief plus a de-identified dataset. **The raw record never leaves
the warehouse.** Everything else is detail.

## Development workflow
- Work in the three legs (`A` grants → `B` masking → `C` Cortex). Legs are additive.
- Commit after every verified leg. Conventional Commits.
- Record every capability verdict in `memory.md` **before** building on it.

## Verification expectations
- SQL: run it in the account and paste the real result. Never assume a function exists.
- App: `.venv/bin/streamlit run app/streamlit_app.py` must start and render without a
  warehouse connection (snapshot mode) and with one (live mode).
- Smoke test: `.venv/bin/python -m pytest tests/ -q`.
- **Never write a ✅ into a capability grid that was not observed.**

## Environment facts (verified 2026-09-06)
- Snowflake account `jjyikad-tgb35242`, user `GAMMATIX`, role `ACCOUNTADMIN`, trial.
- SQL is run through the Snowsight worksheet UI. Programmatic credential setup is
  blocked in this environment, so the app ships dual-mode (see `memory.md`).
- Local venv at `.venv/`. `gh` is authenticated as `ArqamWaheed`.

## Documentation expectations
End every task by updating `plan.md` (state) and `memory.md` (durable knowledge), or
stating explicitly that no update was needed.
