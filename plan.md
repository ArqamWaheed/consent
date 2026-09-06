# plan.md — execution roadmap

**Deadline:** 2026-09-07 06:59 UTC. Target publish 2026-09-06 ~21:00 UTC.
**Spec:** `03-PLAYBOOK-consent.md`.

## Current milestone
**M2 — the pipeline runs for real in Snowflake.**

## Completed
- **M0 Bootstrap** — `memory.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `.env.example`,
  `.gitignore`, `scripts/run.sh`, licence, first commit.
- **M1 Scaffold** — SQL legs A/B/C + fallback drafted, app skeleton, 60 synthetic rows.

## In progress
- **M2 Warehouse** — run `sql/00_gate.sql`, record verdicts, then legs A → B → C.

## Pending, in order
1. **M3 Data** — synthetic rows loadable as pure SQL (`sql/15_load_synthetic.sql`) so the
   repo is self-contained; sample intake PDF for the parse path.
2. **M4 App** — dual-mode Streamlit: live warehouse when credentials exist, labelled
   snapshot otherwise. Split screen + `/status` honesty panel.
3. **M5 Verify** — smoke tests, app renders in both modes, capability grid filled from
   observed results only.
4. **M6 Ship** — public GitHub repo, Apache-2.0, README capability grid, deploy.
5. **M7 Post** — dev.to draft per `../articlewriting/voice.md`. Draft only, never publish.
6. **M8 Media** — cover + inline images, demo screen recording with narration.

## Blockers
- **Programmatic Snowflake credentials cannot be created in this environment** (the
  safety classifier blocks credential setup and non-interactive auth). Consequence: SQL
  is run through the Snowsight worksheet UI, and the deployed app ships in snapshot mode
  until the account owner adds secrets. See `memory.md` → "Credential boundary".

## Architectural next steps
- Keep the app's warehouse access behind one data-access module so snapshot mode and
  live mode are the same call site with two implementations.

## Immediate next action
Run `sql/00_gate.sql` in Snowsight and write the verdicts into `memory.md`.
