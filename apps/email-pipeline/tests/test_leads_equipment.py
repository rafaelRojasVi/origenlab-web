"""Tests for leads equipment tag matching (reuse mart + procurement Spanish)."""

from __future__ import annotations

from origenlab_email_pipeline.leads_equipment import equipment_tags_for_leads, lab_context_signals


def test_empty_input() -> None:
    assert equipment_tags_for_leads("") == []
    assert equipment_tags_for_leads(None) == []  # type: ignore[arg-type]


def test_mart_tags_from_spanish() -> None:
    tags = equipment_tags_for_leads("Necesitamos una balanza analítica y un microscopio.")
    assert "balanza" in tags
    assert "microscopio" in tags


def test_procurement_spanish_phrases() -> None:
    tags = equipment_tags_for_leads("Licitación para centrífuga refrigerada y medidor de humedad.")
    assert "centrifuga" in tags
    assert "humedad_granos" in tags


def test_same_tag_set_as_mart() -> None:
    # Tags should be a subset of mart tag names (no new tag names)
    known = {
        "microscopio",
        "centrifuga",
        "balanza",
        "cromatografia_hplc",
        "phmetro",
        "autoclave",
        "humedad_granos",
        "osmometro",
        "termobalanza",
    }
    tags = equipment_tags_for_leads("balanza analítica, HPLC, pH-metro, autoclave, humedad granos")
    for t in tags:
        assert t in known or t in {"espectrofotometro", "incubadora", "titulador", "liofilizador", "horno_mufla", "pipetas"}


def test_new_equipment_tags() -> None:
    tags = equipment_tags_for_leads("Osmometro y Termobalanza para TGA/termogravimetría y medidor de humedad.")
    assert "osmometro" in tags
    assert "termobalanza" in tags
    assert "humedad_granos" in tags


def test_lab_context_signals_detects_laboratorio() -> None:
    score, tags = lab_context_signals("Servicio para laboratorio clínico y control de calidad")
    assert score > 0.6
    assert "laboratorio" in tags or "laboratorio_clinico" in tags


def test_lab_context_signals_detects_metrologia() -> None:
    score, tags = lab_context_signals("Calibración y metrología de instrumentos de medición")
    assert score > 0.4
    assert "calibracion_metrologia" in tags
