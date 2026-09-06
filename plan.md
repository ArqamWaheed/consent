# plan.md — execution roadmap

**Deadline:** 2026-09-07 06:59 UTC. **Spec:** `03-PLAYBOOK-consent.md` (local only, gitignored).

## Current milestone
**Shipped.** Post published, app live against the warehouse.

**Live app:** https://consent-warehouse.streamlit.app (public, **live mode**)
**Post:** https://dev.to/arqamwd/the-charity-had-the-proof-it-just-couldnt-show-anyone-hdk
**Repo:** https://github.com/ArqamWaheed/consent (public)
**Draft:** saved and unpublished on dev.to, carrying the challenge submission badge.

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

## Done since
- Repo made public and pushed.
- App deployed to Streamlit Community Cloud and verified from a clean headless
  browser with no session: renders correctly, public, no page errors.
- Post updated with the live URL and the `{% github %}` embed (which only validates
  once the repo is public), re-saved as a draft.

## Live mode is on
`CONSENT_APP_SVC` (key-pair, one role, `DEFAULT_SECONDARY_ROLES=()`) is configured in
Streamlit's Secrets. Verified from a clean browser against the public URL: green live
banner, empty secondary roles, and the boundary refusal performed live.

**If the app ever shows the snapshot banner again, reboot it before debugging
anything else.** Streamlit Cloud served pre-`0f1359e` code for a while after the push,
so the secrets bridge was missing and it reported "no credentials configured". A
reboot fixed it.

## Nothing is blocked

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
