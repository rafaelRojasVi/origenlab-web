"""
Unit tests for business filter classification.
"""
from __future__ import annotations

import pytest

from origenlab_email_pipeline.email_business_filters import (
    classify_email,
    in_view_business_only,
    in_view_business_only_external,
    in_view_operational_no_ndr,
    view_filter,
)


def _classify(sender: str = "", recipients: str = "", subject: str = "", body: str = ""):
    return classify_email(sender=sender, recipients=recipients, subject=subject, body=body)


# --- Bounce / NDR ---


def test_mailer_daemon_bounce_ndr():
    r = _classify(sender="MAILER-DAEMON@mail.example.com", subject="Delivery Status")
    assert "bounce_ndr" in r["tags"]
    assert r["primary_category"] == "bounce_ndr"
    assert r["is_bounce"] is True


def test_postmaster_bounce_ndr():
    r = _classify(sender="postmaster@mx.example.com", subject="Undeliverable message")
    assert r["primary_category"] == "bounce_ndr"


def test_delivery_failed_subject_bounce_ndr():
    r = _classify(subject="Mail delivery failed: returning message to sender")
    assert r["primary_category"] == "bounce_ndr"


# --- Social ---


def test_facebook_social_notification():
    r = _classify(sender="notify@facebookmail.com", subject="Someone commented")
    assert "social_notification" in r["tags"]
    assert r["primary_category"] == "social_notification"
    assert r["is_social"] is True


def test_linkedin_social():
    r = _classify(sender="messages-noreply@linkedin.com")
    assert r["primary_category"] == "social_notification"


# --- Logistics ---


def test_dhl_logistics():
    r = _classify(sender="tracking@dhl.com", subject="Your shipment is on the way")
    assert "logistics" in r["tags"]
    assert r["primary_category"] == "logistics"


# --- Marketplace ---


def test_mercadopublico_marketplace():
    r = _classify(sender="licitaciones@mercadopublico.cl", subject="Nueva licitación publicada")
    assert "marketplace" in r["tags"]
    assert r["primary_category"] == "marketplace"


def test_wherex_marketplace():
    r = _classify(sender="sistema@wherex.com", subject="Licitación adjudicada")
    assert "marketplace" in r["tags"]


# --- Institution ---


def test_university_institution():
    r = _classify(sender="decano@uach.cl", body="La universidad informa que...")
    assert "institution" in r["tags"]
    assert r["primary_category"] == "institution"


def test_uc_institution():
    r = _classify(sender="contacto@uc.cl")
    assert "institution" in r["tags"]


# --- Internal ---


def test_labdelivery_internal():
    r = _classify(sender="ventas@labdelivery.cl", subject="Pedido interno")
    assert "internal" in r["tags"]
    assert r["primary_category"] == "internal"
    assert r["is_internal"] is True


# --- Business core ---


def test_quote_email_business_core():
    r = _classify(
        subject="Cotización equipo laboratorio",
        body="Adjunto enviamos cotización solicitada. Plazo de validez 15 días.",
    )
    assert "business_core" in r["tags"]
    assert r["is_business_only_candidate"] is True


def test_invoice_business_core():
    r = _classify(subject="Factura 12345", body="Estimado cliente, adjunto factura.")
    assert "business_core" in r["tags"]


def test_order_business_core():
    r = _classify(subject="Orden de compra OC-2024-001", body="Confirmamos pedido.")
    assert "business_core" in r["tags"]


# --- Spam suspect ---


def test_adult_spam_suspect():
    r = _classify(subject="Adult content warning", body="Click here for adult content")
    assert "spam_suspect" in r["tags"]
    assert r["primary_category"] == "spam_suspect"


# --- Newsletter ---


def test_newsletter_sender():
    r = _classify(sender="newsletter@marketing.com", subject="Weekly digest")
    assert "newsletter" in r["tags"]


# --- Precedence: bounce wins over others ---


def test_bounce_precedence_over_business():
    r = _classify(
        sender="MAILER-DAEMON@host",
        subject="Delivery failed",
        body="Cotización adjunta could not be delivered",
    )
    assert r["primary_category"] == "bounce_ndr"


# --- View predicates ---


def test_view_operational_no_ndr_excludes_bounce():
    bounce = _classify(sender="MAILER-DAEMON@x.com")
    assert in_view_operational_no_ndr(bounce) is False
    business = _classify(subject="Cotización", body="Adjunto cotización")
    assert in_view_operational_no_ndr(business) is True


def test_view_business_only_includes_core_excludes_newsletter():
    business = _classify(subject="Cotización", body="Adjunto cotización")
    assert in_view_business_only(business) is True
    newsletter = _classify(sender="newsletter@x.com", subject="Unsubscribe")
    assert in_view_business_only(newsletter) is False


def test_view_business_only_external_excludes_internal():
    internal = _classify(sender="a@labdelivery.cl", subject="Re: Pedido")
    assert in_view_business_only(internal) is True
    assert in_view_business_only_external(internal) is False
    external = _classify(sender="a@proveedor.com", subject="Cotización")
    assert in_view_business_only_external(external) is True


def test_view_filter_dispatch():
    b = _classify(sender="x@labdelivery.cl", subject="Cotización")
    assert view_filter(b, "all_messages") is True
    assert view_filter(b, "business_only") is True
    assert view_filter(b, "business_only_external") is False
