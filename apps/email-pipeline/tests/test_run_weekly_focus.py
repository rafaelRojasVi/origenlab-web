"""Tests for weekly canonical focus runner."""

from __future__ import annotations

import csv
import importlib.util
import sqlite3
import sys
from pathlib import Path


def _load_script():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "leads" / "run_weekly_focus.py"
    spec = importlib.util.spec_from_file_location("run_weekly_focus", script_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_run_weekly_focus_outputs_csv_and_summary(tmp_path: Path) -> None:
    mod = _load_script()
    db = tmp_path / "test.sqlite"

    from origenlab_email_pipeline.leads_schema import ensure_leads_tables

    conn = sqlite3.connect(str(db))
    ensure_leads_tables(conn)
    conn.execute(
        """
        INSERT INTO lead_master (
          id, source_name, source_type, source_record_id, source_url, org_name,
          buyer_kind, equipment_match_tags, lab_context_score, evidence_summary,
          priority_score, fit_bucket, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1001,
            "chilecompra",
            "procurement",
            "abc",
            "https://example.com/lic",
            "Hospital Test",
            "hospital",
            "autoclave",
            1.0,
            "Licitacion de laboratorio",
            7.2,
            "high_fit",
            "nuevo",
        ),
    )
    conn.execute(
        "INSERT INTO lead_outreach_enrichment (lead_id, enrichment_json, source_file, updated_at) VALUES (?, ?, ?, ?)",
        (1001, '{"nombre_contacto_compras":"Ana"}', "x.csv", "2026-01-01T00:00:00Z"),
    )
    conn.commit()
    conn.close()

    reports = tmp_path / "reports" / "out"
    active = reports / "active"
    active.mkdir(parents=True, exist_ok=True)
    # current + merged without contacts => should trigger warning text
    for name in ("leads_contact_hunt_current.csv", "leads_contact_hunt_current_merged.csv"):
        with (active / name).open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "id_lead",
                    "organizacion_compradora",
                    "nombre_contacto_compras",
                    "email_publico_compras",
                    "telefono_publico_compras",
                ],
            )
            w.writeheader()
            w.writerow(
                {
                    "id_lead": "1001",
                    "organizacion_compradora": "Hospital Test",
                    "nombre_contacto_compras": "",
                    "email_publico_compras": "",
                    "telefono_publico_compras": "",
                }
            )

    out_csv = reports / "leads_weekly_focus.csv"
    out_md = reports / "leads_weekly_focus_summary_es.md"
    argv = [
        "run_weekly_focus.py",
        "--db",
        str(db),
        "--out-csv",
        str(out_csv),
        "--out-summary",
        str(out_md),
        "--top",
        "10",
    ]
    old = sys.argv
    try:
        sys.argv = argv
        code = mod.main()
    finally:
        sys.argv = old
    assert code == 0
    assert out_csv.exists()
    assert out_md.exists()

    txt = out_md.read_text(encoding="utf-8")
    assert "Resumen semanal de foco comercial" in txt
    assert "lead_outreach_enrichment" in txt
    assert "0 filas con contacto" in txt
