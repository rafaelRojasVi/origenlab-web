"""Tests for lead scoring (deterministic, explainable)."""

from __future__ import annotations

import pytest

from origenlab_email_pipeline.leads_score import (
    compute_priority_score,
    fit_bucket,
    score_contact_info,
    score_equipment_match,
    score_lab_context,
    score_procurement_intent,
    score_research_lab_relevance,
    score_source_strength,
)


def test_score_source_strength() -> None:
    assert score_source_strength("procurement") == 2.0
    assert score_source_strength("accredited_lab") == 1.5
    assert score_source_strength("research_center") == 1.0
    assert score_source_strength("unknown") == 0.5
    assert score_source_strength(None) == 0.0
    assert score_source_strength("") == 0.0


def test_score_procurement_intent() -> None:
    assert score_procurement_intent("tender_buyer", "procurement") == 2.0
    assert score_procurement_intent("tender_buyer", "accredited_lab") == 0.0
    assert score_procurement_intent("accredited_lab", "procurement") == 0.0
    assert score_procurement_intent(None, None) == 0.0


def test_score_research_lab_relevance() -> None:
    assert score_research_lab_relevance("accredited_lab", "accredited_lab") == 2.0
    assert score_research_lab_relevance("corfo_center", "research_center") == 1.5
    assert score_research_lab_relevance("tender_buyer", "procurement") == 0.0
    assert score_research_lab_relevance(None, None) == 0.0


def test_score_equipment_match() -> None:
    assert score_equipment_match(None) == 0.0
    assert score_equipment_match("") == 0.0
    assert score_equipment_match("balanza") == 0.5
    assert score_equipment_match("balanza,centrifuga") == 2.0
    assert score_equipment_match("balanza, centrifuga, microscopio") == 2.0


def test_score_contact_info() -> None:
    assert score_contact_info("a@b.cl", None) == 1.0
    assert score_contact_info(None, "+56912345678") == 1.0
    assert score_contact_info("a@b.cl", "123") == 1.0
    assert score_contact_info(None, None) == 0.0
    assert score_contact_info("", "") == 0.0


def test_score_lab_context() -> None:
    assert score_lab_context(None) == 0.0
    assert score_lab_context(0.0) == 0.0
    assert score_lab_context(0.9) == 0.9
    assert score_lab_context(10.0) == 2.0


def test_compute_priority_score_deterministic() -> None:
    score1, reason1 = compute_priority_score("procurement", "tender_buyer", "balanza,centrifuga", 1.0, "universidad", "a@b.cl", None)
    score2, reason2 = compute_priority_score("procurement", "tender_buyer", "balanza,centrifuga", 1.0, "universidad", "a@b.cl", None)
    assert score1 == score2
    assert reason1 == reason2


def test_compute_priority_score_reason_non_empty() -> None:
    score, reason = compute_priority_score("accredited_lab", "accredited_lab", "microscopio", 0.5, None, "x@y.cl", "")
    assert score >= 0
    assert isinstance(reason, str)
    assert len(reason) > 0
    assert "contacto" in reason or "fuente" in reason


def test_fit_bucket_high_fit_with_equipment_and_context() -> None:
    fb = fit_bucket(priority_score=7.2, equipment_match_tags="balanza", lab_context_score=1.0, buyer_kind="hospital")
    assert fb == "high_fit"


def test_fit_bucket_low_fit_generic() -> None:
    fb = fit_bucket(priority_score=4.0, equipment_match_tags=None, lab_context_score=0.0, buyer_kind="publico")
    assert fb == "low_fit"
