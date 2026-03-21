"""Tests for org_normalize (lead account rollup)."""

from __future__ import annotations

from origenlab_email_pipeline.org_normalize import (
    account_dedupe_key,
    better_canonical_name,
    is_junk_org_name,
    normalize_domain,
    normalize_org_name,
)


def test_normalize_org_name_basic() -> None:
    assert normalize_org_name("  Hospital   Regional  ") == "hospital regional"
    assert normalize_org_name("Empresa Demo S.A.") == "empresa demo"


def test_is_junk() -> None:
    assert is_junk_org_name("") is True
    assert is_junk_org_name("n/a") is True
    assert is_junk_org_name("Aceptada") is True
    assert is_junk_org_name("ChileCompra (sin comprador)") is True
    assert is_junk_org_name("Hospital de Talca") is False


def test_normalize_domain() -> None:
    assert normalize_domain("https://WWW.Example.CL/path") == "example.cl"
    assert normalize_domain("mercadopublico.cl") is None


def test_account_dedupe_key() -> None:
    assert account_dedupe_key("hospital x", "hospitalx.cl") == "hospital x||hospitalx.cl"


def test_better_canonical_name() -> None:
    assert better_canonical_name("A", "Longer Name Org") == "Longer Name Org"
    assert better_canonical_name("Already Longer", "Short") == "Already Longer"
