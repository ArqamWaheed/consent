"""Consent — publish your impact without publishing your people.

Presentation only. Every question about where a row came from is answered by
app/warehouse.py, so this file never has to know whether it is talking to a live
Snowflake connection or to the published snapshot.

The app connects as role CONSENT_APP, which has SELECT on three objects and no
access at all to the private table. That is not a policy in a README; it is a grant.
"""
from __future__ import annotations

import io
import csv
import os

import streamlit as st

from warehouse import Case, open_source

# Streamlit Cloud delivers secrets through st.secrets. warehouse.py deliberately
# knows nothing about Streamlit, so bridge them into the environment here, before
# anything asks for a connection. Absent secrets is the normal case, not an error.
try:
    for _key, _value in st.secrets.items():
        if _key.startswith("SNOWFLAKE_") and isinstance(_value, str):
            os.environ.setdefault(_key, _value)
except Exception:  # noqa: BLE001 - no secrets file at all is fine
    pass

st.set_page_config(page_title="Consent", page_icon="🔒", layout="wide")

NEED_ORDER = ["food", "housing", "health", "legal"]


def as_csv(rows: list[Case]) -> str:
    """The de-identified dataset, in the shape a funder can actually be handed."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["case_id", "intake_date", "redacted_note", "need_type", "unresolved"])
    for c in rows:
        writer.writerow([c.case_id, c.intake_date, c.redacted_note, c.need_type, c.unresolved])
    return buf.getvalue()


@st.cache_resource(show_spinner=False)
def _source():
    return open_source()


source, reason = _source()
status = source.status(reason)
cases: list[Case] = source.cases()
brief = source.brief()
boundary = source.boundary_test()
private_rows = source.private_row_count()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Consent")
st.caption("Publish your impact without publishing your people.")
st.markdown(
    "A charity's proof of impact is made of other people's private lives, so the "
    "proof never gets published. **Consent keeps the raw record inside the "
    "warehouse and lets only the redacted truth out.**"
)

if status.mode == "live":
    st.success(f"Live warehouse connection · role `{status.role}`", icon="🔗")
else:
    st.warning(
        f"**Snapshot mode.** {status.note} What you see below is the pipeline's "
        "published output — the only part that was ever allowed to leave the "
        "warehouse — exported from Snowflake and committed to the repository.",
        icon="📄",
    )

st.divider()

left, right = st.columns([1, 1.35], gap="large")

# ── LEFT: what stays in the warehouse ────────────────────────────────────────
with left:
    st.subheader("Stays in the warehouse")
    st.metric("Private records held", private_rows if private_rows is not None else "—")
    st.caption(
        "A count is all this role is allowed to know. `PRIVATE_ROW_COUNT` is a view, "
        "so it runs with its owner's rights: the app learns *how many*, never *who*."
    )

    st.markdown("**The read this app is not allowed to make**")
    st.code("SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1", language="sql")
    if boundary.denied:
        st.error(boundary.message, icon="🚫")
    else:
        st.warning(boundary.message, icon="⚠️")

    st.caption(
        "Not hidden by the interface. Refused by the engine, because of one line "
        "that was never written:"
    )
    st.code(
        "GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;\n"
        "-- deliberately NOT granted: RAW_CASES",
        language="sql",
    )

# ── RIGHT: what may be published ─────────────────────────────────────────────
with right:
    st.subheader("Safe to publish")

    if brief is not None:
        st.markdown("**Impact brief**")
        st.info(brief.text)
        st.caption(
            f"Written by `AI_AGG` across every redacted row · method: `{brief.method}` "
            f"· generated {brief.generated_at}"
        )

    if cases:
        counts = {n: sum(1 for c in cases if c.need_type == n) for n in NEED_ORDER}
        cols = st.columns(len(NEED_ORDER))
        for col, need in zip(cols, NEED_ORDER):
            col.metric(need.title(), counts.get(need, 0))

        st.dataframe(
            [
                {
                    "case": c.case_id,
                    "date": c.intake_date,
                    "redacted note": c.redacted_note,
                    "need": c.need_type,
                    "still open": c.unresolved,
                }
                for c in cases
            ],
            use_container_width=True,
            hide_index=True,
            height=320,
        )
        st.download_button(
            "Download the de-identified dataset (CSV)",
            as_csv(cases),
            "safe_cases.csv",
            "text/csv",
        )
    else:
        st.info("No published rows yet. Run `sql/30_leg_c_cortex.sql`.")

# ── Warehouse status — the honesty panel ─────────────────────────────────────
st.divider()
with st.expander("Warehouse status", expanded=True):
    st.caption(
        "I would rather show you a red light than claim a green one. These are the "
        "verdicts this account actually returns."
    )
    if status.mode == "live":
        st.write(
            f"**Region** `{status.region}` · **Account** `{status.account}` · "
            f"**Role** `{status.role}` · **Version** `{status.version}`"
        )
        st.write(f"**Secondary roles** `{status.secondary_roles or 'none'}`")
        st.caption(
            "Secondary roles matter more than they look. A connection can report "
            "`CURRENT_ROLE() = CONSENT_APP` and still read a table it was never "
            "granted, because every other role the user holds stays active unless "
            "the session runs `USE SECONDARY ROLES NONE`. This app runs it on connect."
        )
        for name, err in status.probes.items():
            if err:
                st.write(f"❌ `{name}` — {err}")
            else:
                st.write(f"✅ `{name}`")
    else:
        st.write(
            "**Not probed live.** These are the verdicts recorded on the account this "
            "was built on, taken *after* granting both halves of the Cortex gate — so "
            "none of the failures below is a missing grant."
        )
        for name, err in status.probes.items():
            if err:
                st.write(f"❌ `{name}` — {err}")
            else:
                st.write(f"✅ `{name}`")
        st.caption(
            "Two of eleven survived. `AI_AGG` and `AI_SUMMARIZE_AGG` are also the two "
            "the docs exempt from needing the `CORTEX_USER` role — the trial gate and "
            "the role gate draw the same line. The pipeline was rebuilt on `AI_AGG`."
        )
