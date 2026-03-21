#!/usr/bin/env python3
"""Match lead_master to organization_master; write results to lead_matches_existing_orgs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from origenlab_email_pipeline.config import load_settings
from origenlab_email_pipeline.db import connect
from origenlab_email_pipeline.leads_match import match_leads_to_mart
from origenlab_email_pipeline.leads_schema import ensure_leads_tables


def main() -> int:
    ap = argparse.ArgumentParser(description="Match leads to existing organization_master")
    ap.add_argument("--db", type=Path, default=None, help="SQLite path (default: from config)")
    args = ap.parse_args()
    settings = load_settings()
    db_path = args.db or settings.resolved_sqlite_path()
    conn = connect(db_path)
    ensure_leads_tables(conn)
    try:
        n = match_leads_to_mart(conn)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    conn.close()
    print(f"Wrote {n} match rows to lead_matches_existing_orgs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
