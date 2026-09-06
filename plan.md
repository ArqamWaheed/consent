# plan.md — execution roadmap

**Deadline:** 2026-09-07 06:59 UTC. **Spec:** `03-PLAYBOOK-consent.md` (local only, gitignored).

## Current milestone
**M7 — handoff. The build is done; three actions need the account owner.**

## Completed
- **M0 Bootstrap** — `memory.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, licence, first commit.
- **M1 Scaffold** — SQL legs drafted, app skeleton, 60 synthetic rows.
- **M2 Warehouse** — gate run against the real account. Nine of eleven AI capabilities
  refused; verdicts and verbatim errors recorded in `memory.md` and the README.
- **M3 Data** — 60 rows loaded and deduplicated in `CONSENT.APP.RAW_CASES`.
- **M4 Pipeline** — Leg C rebuilt on the `AI_AGG` per-row transform. 60/60 rows
  redacted, classified and triaged in 24s. Brief written by `AI_AGG`. Both exported
  to `data/` as the committed snapshot.
- **M5 Security** — boundary test run for real. It FAILED (secondary roles), was
  diagnosed, fixed with `USE SECONDARY ROLES NONE`, and re-verified as refused.
- **M6 App + media** — dual-mode Streamlit app, 10 passing tests, 75s narrated demo
  video, four generated images plus a real screenshot.
- **M7 Post** — dev.to draft saved, unpublished, with cover, tags and all four images.

## Blocked on the account owner (each is one action)
These are blocked by this environment's safety layer, not by the work.
1. **Make the GitHub repo public and push.** `gh repo create consent --public
   --source=. --push`. The post links `github.com/ArqamWaheed/consent`.
2. **Deploy the app** (Streamlit Community Cloud, `app/streamlit_app.py`), then put
   the URL into the post's `## Demo` section, replacing the placeholder line.
3. **Publish the dev.to draft** once 1 and 2 are done.

## Optional, in priority order if there is time
1. **Live mode for the deployed app** — create a Snowflake user restricted to
   `CONSENT_APP`, key-pair auth, put the secrets in Streamlit. The app flips to live
   automatically; nothing to change in code. **Do not grant it any other role** —
   see the secondary-roles note in `memory.md`.
2. Host `demo/consent-demo.mp4` somewhere embeddable and swap it into `## Demo`.
3. `AI_PARSE_DOCUMENT` probe, for grid completeness. Not load-bearing.

## Architectural next steps
None outstanding. The live/snapshot split is behind `app/warehouse.py`; adding
credentials requires no code change.

## Immediate next action
Item 1 above: make the repo public and push.
