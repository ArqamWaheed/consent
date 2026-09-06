"""Consent — publish your impact without publishing your people.

The app connects as role CONSENT_APP, which has SELECT on exactly one table.
It cannot read RAW_CASES. That is not a policy in a README; it is a grant.
"""
import os
import streamlit as st
import snowflake.connector

st.set_page_config(page_title="Consent", page_icon="🔒", layout="wide")

CORTEX_PROBES = {
    "AI_AGG": "SELECT AI_AGG(c,'one word') FROM (SELECT 'x' c)",
    "AI_REDACT": "SELECT AI_REDACT('call Maria on 555-0142')",
    "AI_CLASSIFY": "SELECT AI_CLASSIFY('needs food',['food','housing'])",
    "AI_FILTER": "SELECT AI_FILTER('is this unresolved','rent overdue')",
    "AI_EXTRACT": "SELECT AI_EXTRACT('needs food',{'need':'what they need'})",
}


@st.cache_resource
def connect():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ.get("SNOWFLAKE_ROLE", "CONSENT_APP"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "CONSENT"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "APP"),
    )


def q(sql, params=None):
    with connect().cursor() as cur:
        cur.execute(sql, params or {})
        return cur.fetchall()


st.title("Consent")
st.caption("Publish your impact without publishing your people.")

left, right = st.columns(2)

# ── LEFT: what stays in the warehouse ────────────────────────────────────────
with left:
    st.subheader("Stays in the warehouse")
    try:
        # Deliberately attempted. The failure IS the demo.
        q("SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1")
        st.error("This app could read the private table. That is a bug — check the grants.")
    except Exception as exc:  # noqa: BLE001 — the exception is the product
        st.info("This app's role cannot SELECT this table.")
        st.code(str(exc).strip()[:400], language="text")
    st.metric("Private rows held", q("SELECT COUNT(*) FROM CONSENT.APP.SAFE_CASES")[0][0])
    st.caption("A row count is all this role is allowed to know.")

# ── RIGHT: what you may publish ──────────────────────────────────────────────
with right:
    st.subheader("Safe to publish")
    rows = q(
        "SELECT case_id, intake_date, redacted_note, need_type, unresolved "
        "FROM CONSENT.APP.SAFE_CASES ORDER BY intake_date"
    )
    st.dataframe(
        [
            {"case": r[0], "date": r[1], "note": r[2], "need": r[3], "open": r[4]}
            for r in rows
        ],
        use_container_width=True,
    )
    st.download_button(
        "Download de-identified dataset (CSV)",
        "\n".join(",".join(map(str, r)) for r in rows),
        "safe_cases.csv",
    )

# ── Warehouse status — the honesty panel ─────────────────────────────────────
with st.expander("Warehouse status", expanded=True):
    try:
        region, account, role = q(
            "SELECT CURRENT_REGION(), CURRENT_ACCOUNT(), CURRENT_ROLE()"
        )[0]
        st.write(f"**Region** `{region}` · **Account** `{account}` · **Role** `{role}`")
    except Exception as exc:  # noqa: BLE001
        st.error(f"No warehouse connection: {exc}")

    st.caption("Live probe — I would rather show you a red light than claim a green one.")
    for name, probe in CORTEX_PROBES.items():
        try:
            q(probe)
            st.write(f"✅ `{name}`")
        except Exception as exc:  # noqa: BLE001
            st.write(f"❌ `{name}` — {str(exc).strip()[:120]}")
