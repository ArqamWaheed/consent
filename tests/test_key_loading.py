"""The credential path, tested with a throwaway key generated in the test.

No real key material is involved. This checks the two things that would silently
break the deployed app: that an inline PEM (how Streamlit Cloud supplies it) is
accepted at all, and that a failure never puts key material on screen.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
import warehouse  # noqa: E402


@pytest.fixture
def throwaway_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def test_inline_pem_is_accepted(monkeypatch, throwaway_pem):
    """This is the shape Streamlit Cloud hands us. It has no filesystem to read."""
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY", throwaway_pem)
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_FILE", raising=False)
    der = warehouse._private_key_der()
    assert isinstance(der, bytes) and len(der) > 100


def test_key_file_is_accepted(monkeypatch, throwaway_pem, tmp_path):
    path = tmp_path / "k.p8"
    path.write_text(throwaway_pem)
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_FILE", str(path))
    assert isinstance(warehouse._private_key_der(), bytes)


def test_no_key_configured_is_not_an_error(monkeypatch):
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_FILE", raising=False)
    assert warehouse._private_key_der() is None


def test_errors_never_echo_key_material():
    leaky = "auth failed: -----BEGIN PRIVATE KEY----- MIIEvQIBADAN..."
    assert "BEGIN" not in warehouse._scrub(leaky)
    assert "MIIEvQIBADAN" not in warehouse._scrub(leaky)
    # Ordinary errors must still be readable.
    assert warehouse._scrub("Incorrect username or password") == (
        "Incorrect username or password")


def test_bad_key_falls_back_to_snapshot_without_leaking(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "nonexistent-account")
    monkeypatch.setenv("SNOWFLAKE_USER", "CONSENT_APP_SVC")
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\nnope\n")
    source, reason = warehouse.open_source()
    assert isinstance(source, warehouse.SnapshotSource)
    assert "BEGIN" not in reason
