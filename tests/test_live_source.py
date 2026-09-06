"""Exercise the live warehouse path without a warehouse.

The deployed app runs in snapshot mode, so `LiveSource` would otherwise ship
having never executed a single line. This replays the exact responses and error
strings the real account returned, so the code path at least runs, and the one
statement the boundary depends on is asserted to be issued first.

This is not a substitute for a live connection. It catches shape and ordering
bugs, not Snowflake's actual behaviour.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
import warehouse  # noqa: E402

# Verbatim from the account this was built on.
DENIAL = ("002003 (42S02): SQL compilation error: Object "
          "'CONSENT.APP.RAW_CASES' does not exist or not authorized.")
TRIAL_GATE = "AI function {} is not available for trial accounts."


class FakeCursor:
    def __init__(self, log, rows_for):
        self._log, self._rows_for, self._rows = log, rows_for, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, *_a, **_k):
        self._log.append(sql)
        self._rows = self._rows_for(sql)

    def fetchall(self):
        return self._rows


class FakeConnection:
    """Answers like the real account did, including its refusals."""

    def __init__(self):
        self.log: list[str] = []

    def cursor(self):
        return FakeCursor(self.log, self._rows_for)

    @staticmethod
    def _rows_for(sql: str):
        if "RAW_CASES" in sql:
            raise RuntimeError(DENIAL)
        for fn in ("AI_REDACT", "AI_CLASSIFY", "AI_FILTER", "AI_EXTRACT"):
            if fn in sql:
                raise RuntimeError(TRIAL_GATE.format(fn))
        if "CURRENT_REGION" in sql:
            return [("AWS_US_WEST_2", "POB69176", "CONSENT_APP", "10.31.103",
                     '{"roles":"","value":""}')]
        if "PRIVATE_ROW_COUNT" in sql:
            return [(60,)]
        if "IMPACT_BRIEF" in sql:
            return [("A significant pattern of unmet need...", "cortex",
                     "2026-09-06 04:25:13.306")]
        if "SAFE_CASES" in sql:
            return [(f"CS-{2000 + i}", "2026-09-02", "[NAME] needs a solicitor.",
                     "legal", True) for i in range(60)]
        return [("ok",)]


def test_secondary_roles_are_dropped_before_any_query():
    """The security fix must be the first statement on the connection."""
    con = FakeConnection()
    warehouse.LiveSource(con)
    assert con.log, "no statement was issued on connect"
    assert con.log[0] == "USE SECONDARY ROLES NONE"


def test_boundary_test_reports_the_real_refusal():
    src = warehouse.LiveSource(FakeConnection())
    result = src.boundary_test()
    assert result.denied is True
    assert "does not exist or not authorized" in result.message


def test_live_status_separates_passes_from_trial_gated_failures():
    status = warehouse.LiveSource(FakeConnection()).status()
    assert status.mode == "live"
    assert status.role == "CONSENT_APP"
    assert status.secondary_roles == '{"roles":"","value":""}'
    passed = {k for k, v in status.probes.items() if not v}
    failed = {k for k, v in status.probes.items() if v}
    assert passed == {"AI_AGG", "AI_SUMMARIZE_AGG"}
    assert failed == {"AI_REDACT", "AI_CLASSIFY", "AI_FILTER", "AI_EXTRACT"}


def test_live_reads_parse_into_the_ui_types():
    src = warehouse.LiveSource(FakeConnection())
    cases = src.cases()
    assert len(cases) == 60
    assert isinstance(cases[0], warehouse.Case)
    assert cases[0].unresolved is True
    assert src.private_row_count() == 60
    brief = src.brief()
    assert brief is not None and brief.method == "cortex"


def test_open_source_falls_back_if_dropping_secondary_roles_fails(monkeypatch):
    """If the security statement cannot run, do NOT serve live data anyway."""
    class Hostile(FakeConnection):
        @staticmethod
        def _rows_for(sql):
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        warehouse.LiveSource(Hostile())
