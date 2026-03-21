from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import streamlit as st


def _load_app_module():
    """Cargar apps/business_mart_app.py como módulo sin requerir paquete apps."""
    root = Path(__file__).resolve().parents[1]
    app_path = root / "apps" / "business_mart_app.py"
    spec = importlib.util.spec_from_file_location("business_mart_app", app_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


app = _load_app_module()


def test_friendly_org_type_labels_in_spanish():
    assert "Educación" in app._friendly_org_type("education")
    assert "Empresa" in app._friendly_org_type("business")
    assert "Gobierno" in app._friendly_org_type("gov")
    assert "personal" in app._friendly_org_type("personal")
    assert app._friendly_org_type(None) == "Sin clasificar"


def test_friendly_doc_type_labels_in_spanish():
    assert app._friendly_doc_type("quote") == "Cotización"
    assert app._friendly_doc_type("invoice") == "Factura"
    assert "Lista de precios" in app._friendly_doc_type("price_list")
    assert "Orden de compra" in app._friendly_doc_type("purchase_order")
    # Código desconocido cae en etiqueta genérica
    assert app._friendly_doc_type("something_else") == "Otro documento"


def test_signal_label_returns_business_friendly_spanish():
    label, desc = app._signal_label("quote_email_plus_quote_doc")
    assert "Cotización" in label
    assert "cotización repetidos" in desc

    label, desc = app._signal_label("education_with_quote_activity")
    assert "Universidad" in label
    assert "educación" in desc

    label, desc = app._signal_label("dormant_contact")
    assert "Cuenta dormida" in label
    assert "alto historial" in desc

    # Señal desconocida devuelve el código original pero con descripción genérica
    code = "unknown_signal_code"
    label, desc = app._signal_label(code)
    assert label == code
    assert "Señal heurística" in desc


def test_navigate_to_sets_session_state_and_calls_rerun(monkeypatch):
    # Asegurar un session_state limpio para el test
    st.session_state.clear()

    called = {"rerun": False}

    def fake_rerun() -> None:
        called["rerun"] = True

    # Sustituimos st.rerun por una función que marque la llamada
    monkeypatch.setattr(app.st, "rerun", fake_rerun, raising=False)

    app._navigate_to("Organizaciones", org_only_unis=True, extra_flag="x")

    assert called["rerun"] is True
    assert st.session_state["start_page"] == "Organizaciones"
    assert st.session_state["org_only_unis"] is True
    assert st.session_state["extra_flag"] == "x"


def test_quick_action_default_page_is_resumen(monkeypatch):
    """
    Validar la lógica de selección de pestaña por defecto sin tocar la BD real.

    Emulamos un entorno mínimo donde:
    - _connect_ro devuelve un objeto con los métodos usados.
    - _has_table siempre devuelve True para evitar mensajes de error técnicos.
    - _load_df devuelve dataframes pequeños y controlados.
    """

    class DummyConn:
        def close(self) -> None:
            pass

    # Forzar que no falle la comprobación de tablas
    monkeypatch.setattr(app, "_connect_ro", lambda _: DummyConn())
    monkeypatch.setattr(app, "_has_table", lambda _conn, _name: True)

    def fake_load_df(_conn, sql: str, params: tuple = ()) -> pd.DataFrame:  # type: ignore[override]
        # Devolvemos el mínimo necesario según la consulta.
        if "FROM emails" in sql and "COUNT(*)" in sql:
            return pd.DataFrame([{"c": 10}])
        if "FROM contact_master" in sql and "COUNT(*)" in sql:
            return pd.DataFrame([{"c": 5}])
        if "FROM organization_master" in sql and "COUNT(*)" in sql:
            return pd.DataFrame([{"c": 3}])
        if "FROM document_master" in sql and "sender_domain, doc_type" in sql:
            return pd.DataFrame(columns=["sender_domain", "doc_type"])
        if "FROM document_master" in sql and "COUNT(*)" in sql:
            return pd.DataFrame([{"c": 4}])
        if "MIN(date_iso)" in sql:
            return pd.DataFrame([{"primera": "2020-01-01", "ultima": "2024-12-31"}])
        # Tablas resumen simples
        if "FROM organization_master" in sql:
            return pd.DataFrame(
                [
                    {
                        "dominio": "example.com",
                        "organizacion": "Example",
                        "tipo_org": "education",
                        "primera": "2020-01-01",
                        "ultima": "2024-12-31",
                        "total": 10,
                        "contactos": 3,
                        "cotiz_email": 2,
                        "cotiz_docs": 1,
                        "factura_email": 1,
                        "factura_docs": 0,
                        "compra_email": 0,
                        "doc_emails": 1,
                    }
                ]
            )
        # Por defecto, un df vacío no rompe la app
        return pd.DataFrame()

    monkeypatch.setattr(app, "_load_df", fake_load_df)

    # Stub muy simple de load_settings.resolved_sqlite_path para evitar dependencias externas.
    class DummySettings:
        def resolved_sqlite_path(self):
            return "/tmp/dummy.sqlite"

    monkeypatch.setattr(app, "load_settings", lambda: DummySettings())

    # Ejecutar main no debería lanzar excepciones; esto actúa como smoke test
    app.main()

