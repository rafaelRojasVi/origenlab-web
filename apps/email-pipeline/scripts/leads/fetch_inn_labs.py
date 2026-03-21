#!/usr/bin/env python3
"""Ingest INN accredited labs from a local CSV into external_leads_raw."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from origenlab_email_pipeline.config import load_settings
from origenlab_email_pipeline.db import connect
from origenlab_email_pipeline.leads_ingest import SOURCE_INN_LABS, insert_raw
from origenlab_email_pipeline.leads_schema import ensure_leads_tables

# Expected CSV columns (any can be missing): nombre, lab_name, organizacion, laboratorio, area, esquema, acreditacion,
# region, ciudad, city, sitio, website, url, email, contacto_email, contacto, telefono, phone, id, codigo


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest INN labs from CSV into external_leads_raw")
    ap.add_argument("--file", "-f", type=Path, required=True, help="Path to CSV file")
    ap.add_argument("--db", type=Path, default=None, help="SQLite path (default: from config)")
    args = ap.parse_args()
    if not args.file.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1
    settings = load_settings()
    db_path = args.db or settings.resolved_sqlite_path()
    conn = connect(db_path)
    ensure_leads_tables(conn)
    with open(args.file, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for i, raw in enumerate(rows):
        record_id = str(raw.get("id") or raw.get("codigo") or raw.get("nombre") or raw.get("lab_name") or i)
        source_url = raw.get("url") or raw.get("link") or raw.get("sitio") or raw.get("website") or ""
        insert_raw(conn, source_name=SOURCE_INN_LABS, source_record_id=record_id, raw_json=dict(raw), source_url=source_url or None)
    conn.commit()
    conn.close()
    print(f"Inserted/updated {len(rows)} INN labs raw records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
