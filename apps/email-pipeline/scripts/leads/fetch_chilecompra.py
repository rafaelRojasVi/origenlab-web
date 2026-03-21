#!/usr/bin/env python3
"""Ingest ChileCompra / Mercado Público data from a local file (CSV or JSON) into external_leads_raw."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from origenlab_email_pipeline.config import load_settings
from origenlab_email_pipeline.db import connect
from origenlab_email_pipeline.leads_ingest import SOURCE_CHILECOMPRA, insert_raw
from origenlab_email_pipeline.leads_schema import ensure_leads_tables


def _load_json(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "results", "items", "licitaciones", "records"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return []


def _normalize_header_key(k: str | None) -> str:
    if k is None:
        return ""
    return str(k).strip().lstrip("\ufeff")


def _load_csv(path: Path) -> list[dict]:
    """Load CSV; Mercado Público / ChileCompra bulk exports use ``;`` delimiters."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(65536)
        f.seek(0)
        semi = sample.count(";")
        comma = sample.count(",")
        delimiter = ";" if semi > comma else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        rows: list[dict] = []
        for row in reader:
            if not row:
                continue
            clean = {_normalize_header_key(k): v for k, v in row.items() if k is not None}
            rows.append(clean)
        return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest ChileCompra data from file into external_leads_raw")
    ap.add_argument("--file", "-f", type=Path, required=True, help="Path to CSV or JSON file")
    ap.add_argument("--db", type=Path, default=None, help="SQLite path (default: from config)")
    args = ap.parse_args()
    if not args.file.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1
    settings = load_settings()
    db_path = args.db or settings.resolved_sqlite_path()
    conn = connect(db_path)
    ensure_leads_tables(conn)
    suffix = args.file.suffix.lower()
    if suffix == ".json":
        rows = _load_json(args.file)
    elif suffix == ".csv":
        rows = _load_csv(args.file)
    else:
        print("Error: expected .json or .csv file", file=sys.stderr)
        return 1
    for i, raw in enumerate(rows):
        if not isinstance(raw, dict):
            continue
        # Prefer line-level ids (Codigo / Correlativo) so multi-line tenders do not collapse on CodigoExterno.
        record_id = str(
            raw.get("Codigo")
            or raw.get("Correlativo")
            or raw.get("id")
            or raw.get("codigo")
            or raw.get("tender_id")
            or raw.get("CodigoExterno")
            or i
        )
        source_url = raw.get("url") or raw.get("link") or raw.get("Url") or raw.get("Link") or ""
        insert_raw(conn, source_name=SOURCE_CHILECOMPRA, source_record_id=record_id, raw_json=raw, source_url=source_url or None)
    conn.commit()
    conn.close()
    print(f"Inserted/updated {len(rows)} ChileCompra raw records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
