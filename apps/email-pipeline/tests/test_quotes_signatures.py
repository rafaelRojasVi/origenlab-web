"""
Tests for Phase 2.2 quote and signature handling:
- full_body_clean normalization
- top_reply_clean for various reply/signature patterns.
"""
from __future__ import annotations

from email.mime.text import MIMEText

from origenlab_email_pipeline.parse_mbox import (
    extract_body_structured,
    extract_full_and_top_reply,
)


def _make_plain_message(body: str) -> MIMEText:
    msg = MIMEText(body, "plain", _charset="utf-8")
    msg["Subject"] = "Test"
    return msg


def test_full_and_top_reply_no_quotes_no_signature():
    body = "Estimada,\n\nAdjunto factura 123.\n\nGracias."
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert full_body == body
    assert top_reply == body


def test_english_reply_header_stripped():
    body = (
        "Hi,\n\nHere is the quote you requested.\n\n"
        "On Mon, 1 Jan 2024 at 10:00, Someone <x@example.com> wrote:\n"
        "> Previous content\n"
    )
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert "quote you requested" in top_reply
    assert "On Mon" not in top_reply
    assert "> Previous content" not in top_reply


def test_spanish_reply_header_stripped():
    body = (
        "Hola,\n\nAdjunto OC.\n\n"
        "El 1 de enero de 2024, Juan Pérez escribió:\n"
        "> Texto anterior\n"
    )
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert "Adjunto OC." in top_reply
    assert "escribió" not in top_reply
    assert "> Texto anterior" not in top_reply


def test_outlook_original_message_separator():
    body = (
        "Estimado,\n\nEnvío factura.\n\n"
        "-----Original Message-----\n"
        "From: x@example.com\n"
        "Sent: Monday\n"
        "To: y@example.com\n"
    )
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert "Envío factura." in top_reply
    assert "Original Message" not in top_reply


def test_signature_block_stripped():
    body = (
        "Hola Tatiana,\n\nAdjunto factura y guía.\n\n"
        "Saludos cordiales,\n"
        "Juan Pérez\n"
        "Empresa XYZ\n"
    )
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert "Adjunto factura y guía." in top_reply
    assert "Saludos cordiales" not in top_reply
    assert "Juan Pérez" not in top_reply


def test_short_client_reply_not_overstripped():
    body = "Ok, gracias.\n\nSaludos"
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    # Heuristics may treat trailing "Saludos" as signature; ensure main text is preserved.
    assert "Ok, gracias." in top_reply


def test_top_reply_falls_back_when_no_patterns():
    body = "Solo un mensaje corto sin respuestas ni firmas."
    msg = _make_plain_message(body)
    structured = extract_body_structured(msg)
    full_body, top_reply = extract_full_and_top_reply(structured)
    assert top_reply == full_body

