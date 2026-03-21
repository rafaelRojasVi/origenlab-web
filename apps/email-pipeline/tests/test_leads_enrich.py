from __future__ import annotations

from origenlab_email_pipeline.leads_enrich import (
    derive_outreach_strategy,
    derive_product_angle,
    guess_official_site_and_domain,
)


def test_derive_product_angle_with_equipment_and_hospital() -> None:
    angle, interest, why = derive_product_angle(
        source_name="chilecompra",
        buyer_kind="hospital",
        organization_type_guess="government",
        equipment_match_tags="balanza,centrifuga",
        lab_context_tags="laboratorio,analisis_quimico",
        evidence_summary="Licitación de balanza analítica para laboratorio clínico.",
    )
    assert "balanza" in interest.lower()
    assert "hospital" in angle.lower()
    assert "Licitación" in why or "licitación" in why.lower()


def test_derive_outreach_strategy_hospital_procurement_first() -> None:
    s = derive_outreach_strategy(
        source_name="chilecompra",
        buyer_kind="hospital",
        lead_type="tender_buyer",
        equipment_match_tags="balanza",
        lab_context_tags="laboratorio",
    )
    assert "Compras" in s or "compras" in s
    assert "hospital" in s.lower()


def test_guess_official_site_and_domain_ignores_marketplace() -> None:
    site, dom = guess_official_site_and_domain(
        lead_website="https://www.mercadopublico.cl/fichaLicitacion.html?idLicitacion=1234-1-LR25",
        lead_domain="mercadopublico.cl",
        match_domain="hospital.cl",
    )
    # Should fall back to matched org domain, not marketplace.
    assert dom == "hospital.cl"
    assert "hospital.cl" in (site or "")

