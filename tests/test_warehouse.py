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
    assert status.probes == {}, "snapshot mode must not report probe verdicts it never ran"


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
