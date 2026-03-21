"""Tests for normalizing raw lead rows (ChileCompra, INN, CORFO)."""

from __future__ import annotations

from origenlab_email_pipeline.leads_normalize import (
    normalize_chilecompra,
    normalize_corfo_centers,
    normalize_inn_labs,
    pick_contact_field_for_upsert,
    raw_to_normalized,
)
from origenlab_email_pipeline.leads_ingest import SOURCE_CHILECOMPRA, SOURCE_INN_LABS, SOURCE_CORFO_CENTERS


def test_normalize_chilecompra_minimal() -> None:
    raw = {"titulo": "Balanza analítica", "comprador": "Hospital Regional"}
    out = normalize_chilecompra(raw)
    assert out["source_name"] == SOURCE_CHILECOMPRA
    assert out["source_type"] == "procurement"
    assert out["lead_type"] == "tender_buyer"
    assert "Hospital" in (out["org_name"] or "")
    assert "balanza" in (out["equipment_match_tags"] or "").lower()
    assert out["status"] == "nuevo"


def test_normalize_chilecompra_with_contact() -> None:
    raw = {"titulo": "Microscopio", "comprador": "U Chile", "contacto_email": "compras@uchile.cl"}
    out = normalize_chilecompra(raw)
    assert out["email"] == "compras@uchile.cl"
    assert out["domain"] == "uchile.cl"
    assert out["organization_type_guess"] == "education"


def test_normalize_chilecompra_mercadopublico_bulk_columns() -> None:
    """Bulk CSV columns (semicolon export) map to buyer + region."""
    raw = {
        "Codigo": "9482500",
        "CodigoExterno": "2277-2-LR25",
        "Nombre": "RENOVACIÓN DE CENTRO COMUNITARIO",
        "NombreOrganismo": "MUNICIPALIDAD DE PUDAHUEL",
        "NombreUnidad": "UNIDAD DE LICITACIONES DE PUDAHUEL",
        "Link": "http://www.mercadopublico.cl/fichaLicitacion.html?idLicitacion=2277-2-LR25",
        "RegionUnidad": "Región Metropolitana de Santiago",
        "ComunaUnidad": "Pudahuel",
    }
    out = normalize_chilecompra(raw)
    assert out["source_record_id"] == "9482500"
    assert "MUNICIPALIDAD DE PUDAHUEL" in (out["org_name"] or "")
    assert out["region"] == "Región Metropolitana de Santiago"
    assert out["city"] == "Pudahuel"
    assert "fichaLicitacion" in (out["source_url"] or "")


def test_normalize_inn_labs_minimal() -> None:
    raw = {"nombre": "Lab QA Norte", "area": "Microbiología alimentos", "region": "Metropolitana"}
    out = normalize_inn_labs(raw)
    assert out["source_name"] == SOURCE_INN_LABS
    assert out["source_type"] == "accredited_lab"
    assert out["lead_type"] == "accredited_lab"
    assert "Lab QA Norte" in (out["org_name"] or "")
    assert "INN" in (out["evidence_summary"] or "")


def test_normalize_corfo_centers_minimal() -> None:
    raw = {"centro": "Centro I+D Alimentos", "organizacion": "Universidad de Santiago", "region": "Metropolitana"}
    out = normalize_corfo_centers(raw)
    assert out["source_name"] == SOURCE_CORFO_CENTERS
    assert out["source_type"] == "research_center"
    assert out["lead_type"] == "corfo_center"
    assert "Universidad" in (out["org_name"] or "") or "Centro" in (out["org_name"] or "")


def test_pick_contact_field_for_upsert() -> None:
    assert pick_contact_field_for_upsert("a@b.cl", "old@x.cl") == "a@b.cl"
    assert pick_contact_field_for_upsert("", "old@x.cl") == "old@x.cl"
    assert pick_contact_field_for_upsert(None, "old@x.cl") == "old@x.cl"
    assert pick_contact_field_for_upsert("  ", None) is None
    assert pick_contact_field_for_upsert(None, None) is None


def test_raw_to_normalized_dispatch() -> None:
    out = raw_to_normalized(SOURCE_CHILECOMPRA, {"titulo": "T1", "comprador": "Org"})
    assert out["source_name"] == SOURCE_CHILECOMPRA
    out = raw_to_normalized(SOURCE_INN_LABS, {"nombre": "L1"})
    assert out["source_name"] == SOURCE_INN_LABS
    out = raw_to_normalized(SOURCE_CORFO_CENTERS, {"centro": "C1"})
    assert out["source_name"] == SOURCE_CORFO_CENTERS
