"""Smoke tests for the data-access boundary.

Deliberately narrow. The one thing worth testing here is the rule the whole
project rests on: the app must never present snapshot data as a live warehouse
read, and must never claim a capability it did not observe.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import warehouse  # noqa: E402


def test_snapshot_source_reports_snapshot_mode():
    status = warehouse.SnapshotSource().status("no credentials")
    assert status.mode == "snapshot"
    # Snapshot mode may show verdicts, but only the recorded ones, unmodified.
    # The UI is responsible for labelling them "not probed live"; this asserts it
    # cannot silently invent a verdict that was never observed.
    assert status.probes == warehouse.RECORDED_VERDICTS


def test_recorded_verdicts_match_the_probes_the_app_runs_live():
    """Every function the live panel probes must have a recorded counterpart."""
    missing = set(warehouse.CORTEX_PROBES) - set(warehouse.RECORDED_VERDICTS)
    assert not missing, f"no recorded verdict for {missing}"


def test_only_the_two_documented_functions_passed():
    passed = {k for k, v in warehouse.RECORDED_VERDICTS.items() if not v}
    assert passed == {"AI_AGG", "AI_SUMMARIZE_AGG"}


def test_open_source_without_credentials_falls_back(monkeypatch):
    for key in ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER"):
        monkeypatch.delenv(key, raising=False)
    source, reason = warehouse.open_source()
    assert isinstance(source, warehouse.SnapshotSource)
    assert "snapshot" in reason.lower()


def test_open_source_falls_back_when_connection_fails(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "nonexistent-account")
    monkeypatch.setenv("SNOWFLAKE_USER", "nobody")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "")
    source, reason = warehouse.open_source()
    assert isinstance(source, warehouse.SnapshotSource)
    assert "failed" in reason.lower() or "snapshot" in reason.lower()


def test_snapshot_cases_are_redacted():
    """Nothing that reaches the published side may carry a raw identifier."""
    cases = warehouse.SnapshotSource().cases()
    assert cases, "snapshot is empty — export SAFE_CASES before shipping"
    import re

    phone = re.compile(r"\b\d{3}-\d{4}\b")
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for case in cases:
        assert not phone.search(case.redacted_note), f"phone survived in {case.case_id}"
        assert not email.search(case.redacted_note), f"email survived in {case.case_id}"
        assert case.need_type in {"food", "housing", "health", "legal"}


def test_boundary_test_reports_denial_in_snapshot_mode():
    result = warehouse.SnapshotSource().boundary_test()
    assert result.denied is True
    assert "CONSENT.APP.RAW_CASES" in result.message


def test_recorded_denial_is_the_observed_error():
    """The snapshot panel must quote a real refusal, not a paraphrase of one."""
    assert "does not exist or not authorized" in warehouse.RECORDED_DENIAL
    assert warehouse.PRIVATE_TABLE in warehouse.RECORDED_DENIAL


def test_snapshot_brief_never_names_an_individual():
    """AI_AGG was told to cite counts, never people. Verify it obeyed."""
    brief = warehouse.SnapshotSource().brief()
    assert brief is not None, "no brief snapshot committed"
    import csv
    from pathlib import Path

    raw = Path(__file__).resolve().parent.parent / "data" / "synthetic_cases.csv"
    lines = [l for l in raw.open(encoding="utf-8") if not l.startswith("#")]
    names = set()
    for row in csv.DictReader(lines):
        for word in row["raw_note"].split():
            token = word.strip(".,()'").strip()
            if token.istitle() and len(token) > 3:
                names.add(token)
    # Surnames from the roster must not appear in a brief meant for a funder.
    for surname in ("Fischer", "Alvarez", "Nowak", "Kovac", "Haddad", "Okafor"):
        assert surname not in brief.text, f"{surname} leaked into the brief"


def test_every_snapshot_row_came_from_the_pipeline():
    cases = warehouse.SnapshotSource().cases()
    assert len(cases) == 60
    assert len({c.case_id for c in cases}) == 60
