#!/usr/bin/env python3
"""SQLite → JSONL. Paths from .env / ORIGENLAB_*."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from origenlab_email_pipeline.config import load_settings
from origenlab_email_pipeline.export_jsonl import export_jsonl


def main() -> None:
    settings = load_settings()
    db_path = settings.resolved_sqlite_path()
    out_path = settings.resolved_jsonl_path()

    if not db_path.is_file():
        print(f"SQLite DB not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    n = export_jsonl(db_path, out_path)
    print(f"Wrote {n} lines to {out_path}")


if __name__ == "__main__":
    main()
