"""Where rows come from.

The UI talks to this module and to nothing else about data access, so the two
modes — a live warehouse connection, and a published snapshot — are one call site
with two implementations.

The honest rule this module enforces: **snapshot mode is never dressed up as live
mode.** `Status.mode` is derived from whether a connection actually succeeded, not
from configuration, and the UI prints it either way.
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_CASES = REPO_ROOT / "data" / "safe_cases_snapshot.csv"
SNAPSHOT_BRIEF = REPO_ROOT / "data" / "impact_brief_snapshot.json"

# Probed live in the status panel. The point is to show red lights, not hide them.
CORTEX_PROBES: dict[str, str] = {
    "AI_AGG": "SELECT AI_AGG(c,'reply with one word') FROM (SELECT 'x' c)",
    "AI_SUMMARIZE_AGG": "SELECT AI_SUMMARIZE_AGG(c) FROM (SELECT 'no food' c)",
    "AI_REDACT": "SELECT AI_REDACT('call Maria on 555-0142')",
    "AI_CLASSIFY": "SELECT AI_CLASSIFY('needs food',['food','housing'])",
    "AI_FILTER": "SELECT AI_FILTER('is this unresolved')",
    "AI_EXTRACT": "SELECT AI_EXTRACT('needs food',{'need':'what they need'})",
}

PRIVATE_TABLE = "CONSENT.APP.RAW_CASES"

# Verdicts observed on the account this was built on, after BOTH halves of the
# Cortex gate were granted. Shown in snapshot mode, labelled as recorded rather
# than probed, so the honesty panel is never blank and never overstated.
RECORDED_VERDICTS: dict[str, str] = {
    "AI_AGG": "",
    "AI_SUMMARIZE_AGG": "",
    "AI_REDACT": "AI function _AI_REDACT is not available for trial accounts.",
    "AI_CLASSIFY": "AI function AI_CLASSIFY is not available for trial accounts.",
    "AI_FILTER": "AI function _AI_FILTER_WITH_PROMPT is not available for trial accounts.",
    "AI_EXTRACT": "AI function _AI_EXTRACT is not available for trial accounts.",
    "AI_COMPLETE":
        "AI function _COMPLETE_WITH_PROMPT_HISTORY_LLM is not available for trial accounts.",
    "SNOWFLAKE.CORTEX.SENTIMENT":
        "AI function SENTIMENT is not available for trial accounts.",
    "MASKING POLICY (Enterprise Edition)": "Unsupported feature 'MASKING POLICY'.",
}

# The verbatim refusal this account returns, recorded live. Shown in snapshot mode
# so the panel quotes an observed result rather than describing one.
RECORDED_DENIAL = (
    "SQL compilation error: Object 'CONSENT.APP.RAW_CASES' does not exist or not "
    "authorized."
)


@dataclass(frozen=True)
class Case:
    case_id: str
    intake_date: str
    redacted_note: str
    need_type: str
    unresolved: bool


@dataclass(frozen=True)
class Brief:
    text: str
    method: str
    generated_at: str


@dataclass(frozen=True)
class BoundaryTest:
    """What happened when the app deliberately tried to read the private table."""

    denied: bool
    message: str


@dataclass(frozen=True)
class Status:
    mode: str                      # "live" or "snapshot"
    region: str = ""
    account: str = ""
    role: str = ""
    version: str = ""
    secondary_roles: str = ""
    note: str = ""
    probes: dict[str, str] = field(default_factory=dict)   # name -> "" if ok else error


class SnapshotSource:
    """Reads the published side of the boundary from files in the repo.

    This is not a simulation of the pipeline. It is the pipeline's *output* — the
    only part that was ever allowed to leave the warehouse — checked into the repo
    the same way it would be handed to a funder.
    """

    mode = "snapshot"

    def status(self, reason: str = "") -> Status:
        return Status(mode="snapshot", note=reason, probes=dict(RECORDED_VERDICTS))

    def cases(self) -> list[Case]:
        if not SNAPSHOT_CASES.exists():
            return []
        with SNAPSHOT_CASES.open(newline="", encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(_uncommented(fh))]
        return [
            Case(
                case_id=r["case_id"],
                intake_date=r["intake_date"],
                redacted_note=r["redacted_note"],
                need_type=r["need_type"],
                unresolved=str(r["unresolved"]).strip().lower() in {"true", "1", "t"},
            )
            for r in rows
        ]

    def brief(self) -> Brief | None:
        if not SNAPSHOT_BRIEF.exists():
            return None
        data = json.loads(SNAPSHOT_BRIEF.read_text(encoding="utf-8"))
        return Brief(
            text=data["brief"], method=data["method"], generated_at=data["generated_at"]
        )

    def private_row_count(self) -> int | None:
        brief = self.brief()
        return None if brief is None else int(
            json.loads(SNAPSHOT_BRIEF.read_text(encoding="utf-8")).get("private_rows", 0)
        )

    def boundary_test(self) -> BoundaryTest:
        return BoundaryTest(
            denied=True,
            message=(
                "Not connected, so this is not a live refusal. Recorded from the "
                f"account this was built on, as role CONSENT_APP: {RECORDED_DENIAL}"
            ),
        )


class LiveSource:
    """Reads from Snowflake as role CONSENT_APP, which has SELECT on three objects."""

    mode = "live"

    def __init__(self, connection) -> None:
        self._con = connection
        self._drop_secondary_roles()

    def _drop_secondary_roles(self) -> None:
        """Make the connection's role the ONLY role it has.

        `role=CONSENT_APP` on the connection sets the *primary* role. It does not
        drop the others. Snowflake activates every role the user holds as secondary
        roles, and authorization considers those too — so a connection that reports
        `CURRENT_ROLE() = CONSENT_APP` can still read a table only ACCOUNTADMIN was
        granted. Observed on the account this was built on: the same SELECT returned
        the private note before this statement and was refused after it.

        Without this line the boundary is decorative.
        """
        with self._con.cursor() as cur:
            cur.execute("USE SECONDARY ROLES NONE")

    def _rows(self, sql: str) -> list[tuple]:
        with self._con.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def status(self, reason: str = "") -> Status:
        region, account, role, version, secondary = self._rows(
            "SELECT CURRENT_REGION(), CURRENT_ACCOUNT(), CURRENT_ROLE(), "
            "CURRENT_VERSION(), CURRENT_SECONDARY_ROLES()"
        )[0]
        probes: dict[str, str] = {}
        for name, sql in CORTEX_PROBES.items():
            try:
                self._rows(sql)
                probes[name] = ""
            except Exception as exc:                       # noqa: BLE001
                probes[name] = _short(exc)
        return Status(
            mode="live",
            region=str(region),
            account=str(account),
            role=str(role),
            version=str(version),
            secondary_roles=str(secondary),
            probes=probes,
        )

    def cases(self) -> list[Case]:
        rows = self._rows(
            "SELECT case_id, intake_date, redacted_note, need_type, unresolved "
            "FROM CONSENT.APP.SAFE_CASES ORDER BY intake_date, case_id"
        )
        return [
            Case(str(r[0]), str(r[1]), str(r[2]), str(r[3]), bool(r[4])) for r in rows
        ]

    def brief(self) -> Brief | None:
        rows = self._rows(
            "SELECT brief, method, generated_at FROM CONSENT.APP.IMPACT_BRIEF LIMIT 1"
        )
        if not rows:
            return None
        return Brief(str(rows[0][0]), str(rows[0][1]), str(rows[0][2]))

    def private_row_count(self) -> int | None:
        # A view, so it runs with its owner's rights. The app learns how many
        # private records exist without being able to read one of them.
        return int(self._rows("SELECT private_rows FROM CONSENT.APP.PRIVATE_ROW_COUNT")[0][0])

    def boundary_test(self) -> BoundaryTest:
        """Deliberately attempt the read that must fail. The failure is the product."""
        try:
            self._rows(f"SELECT raw_note FROM {PRIVATE_TABLE} LIMIT 1")
        except Exception as exc:                           # noqa: BLE001
            return BoundaryTest(denied=True, message=_short(exc, 300))
        return BoundaryTest(
            denied=False,
            message=(
                "This app just read the private table. That is a bug in the grants, "
                "not a feature — see sql/10_leg_a_grants.sql."
            ),
        )


def _private_key_der() -> bytes | None:
    """Load the key material, from an inline PEM or a file, as DER for the connector.

    Streamlit Cloud has no filesystem to point at, so the deployed app supplies the
    key inline as `SNOWFLAKE_PRIVATE_KEY`. Locally a path is easier, so both work.
    Nothing here is ever logged or returned.
    """
    from cryptography.hazmat.primitives import serialization

    pem = os.environ.get("SNOWFLAKE_PRIVATE_KEY")
    if pem:
        raw = pem.strip().encode()
    else:
        path = os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE")
        if not path:
            return None
        raw = Path(path).read_bytes()

    passphrase = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE") or None
    key = serialization.load_pem_private_key(
        raw, password=passphrase.encode() if passphrase else None
    )
    return key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def open_source() -> tuple[SnapshotSource | LiveSource, str]:
    """Return the best available source, plus why it was chosen.

    Falls back to the snapshot on any failure, and says so. It never pretends.
    """
    required = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER")
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return SnapshotSource(), (
            "No warehouse credentials configured, so this is the published snapshot."
        )
    try:
        import snowflake.connector

        con = snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ.get("SNOWFLAKE_PASSWORD") or None,
            private_key=_private_key_der(),
            role=os.environ.get("SNOWFLAKE_ROLE", "CONSENT_APP"),
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.environ.get("SNOWFLAKE_DATABASE", "CONSENT"),
            schema=os.environ.get("SNOWFLAKE_SCHEMA", "APP"),
            login_timeout=20,
        )
        return LiveSource(con), "Connected to the warehouse."
    except Exception as exc:                               # noqa: BLE001
        return SnapshotSource(), (
            f"Warehouse connection failed, showing the snapshot: {_scrub(_short(exc))}"
        )


def _scrub(text: str) -> str:
    """Never let key material reach the screen, whatever an exception carries."""
    if "PRIVATE KEY" in text or "BEGIN" in text:
        return "connection error suppressed because it echoed key material"
    return text


def _short(exc: Exception, limit: int = 160) -> str:
    text = " ".join(str(exc).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _uncommented(lines) -> list[str]:
    return [line for line in lines if not line.startswith("#")]
