"""Stream emails table to JSONL (UTF-8)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import orjson


def export_jsonl(db_path: Path, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            """
            SELECT id, source_file, folder, message_id, subject, sender, recipients,
                   date_raw, date_iso, body,
                   COALESCE(body_html, '') AS body_html
            FROM emails
            ORDER BY id
            """
        )
        count = 0
        with out_path.open("wb") as f:
            for row in cur:
                obj = {
                    "id": row["id"],
                    "source_file": row["source_file"],
                    "folder": row["folder"],
                    "message_id": row["message_id"],
                    "subject": row["subject"],
                    "sender": row["sender"],
                    "recipients": row["recipients"],
                    "date_raw": row["date_raw"],
                    "date_iso": row["date_iso"],
                    "body": row["body"],
                    "body_html": row["body_html"],
                }
                f.write(orjson.dumps(obj, option=orjson.OPT_APPEND_NEWLINE))
                count += 1
        return count
    finally:
        conn.close()
