#!/usr/bin/env python3
"""Mbox → SQLite. Paths from .env / ORIGENLAB_* (see .env.example)."""
from __future__ import annotations

import sys
from pathlib import Path

# Repo root on path when run as scripts/02_...
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from origenlab_email_pipeline.config import load_settings
from origenlab_email_pipeline.db import (
    connect,
    init_schema,
    insert_attachment,
    insert_email,
)
from origenlab_email_pipeline.parse_mbox import (
    body_content,
    date_iso_from_msg,
    extract_body_structured,
    extract_full_and_top_reply,
    open_mbox,
    recipients_header,
    walk_attachments,
)
from tqdm import tqdm


def is_probably_mbox(path: Path) -> bool:
    if not path.is_file():
        return False
    # readpst often names mbox files without extension or as mbox
    if path.suffix.lower() in (".mbox", ""):
        return True
    try:
        with path.open("rb") as f:
            head = f.read(512)
        return head.startswith(b"From ") or b"From " in head[:200]
    except OSError:
        return False


def main() -> None:
    settings = load_settings()
    mbox_root = settings.resolved_mbox_dir()
    db_path = settings.resolved_sqlite_path()

    if not mbox_root.is_dir():
        print(f"Mbox directory missing: {mbox_root}", file=sys.stderr)
        sys.exit(1)

    files = [p for p in mbox_root.rglob("*") if p.is_file() and is_probably_mbox(p)]
    if not files:
        print(f"No mbox-like files under: {mbox_root}", file=sys.stderr)
        sys.exit(1)

    conn = connect(db_path)
    init_schema(conn)
    conn.execute("DELETE FROM emails")
    conn.commit()
    total_inserted = 0

    for mbox_path in tqdm(files, desc="mbox files"):
        mbox = open_mbox(str(mbox_path))
        if mbox is None:
            continue
        try:
            for msg in mbox:
                try:
                    body, body_html = body_content(msg)
                    structured = extract_body_structured(msg)
                    full_body_clean, top_reply_clean = extract_full_and_top_reply(structured)
                    attachments = walk_attachments(msg)
                    email_id = insert_email(
                        conn,
                        source_file=str(mbox_path),
                        folder=str(mbox_path.parent),
                        message_id=msg.get("Message-ID"),
                        subject=msg.get("Subject"),
                        sender=msg.get("From"),
                        recipients=recipients_header(msg),
                        date_raw=msg.get("Date"),
                        date_iso=date_iso_from_msg(msg),
                        body=body,
                        body_html=body_html,
                        body_text_raw=structured["body_text_raw"],
                        body_text_clean=structured["body_text_clean"],
                        body_source_type=structured["body_source_type"],
                        body_has_plain=structured["body_has_plain"],
                        body_has_html=structured["body_has_html"],
                        full_body_clean=full_body_clean,
                        top_reply_clean=top_reply_clean,
                        attachment_count=len(attachments),
                        has_attachments=bool(attachments),
                    )
                    for att in attachments:
                        try:
                            insert_attachment(
                                conn,
                                email_id=email_id,
                                part_index=att["part_index"],
                                filename=att["filename"],
                                content_type=att["content_type"],
                                content_disposition=att["content_disposition"],
                                size_bytes=att["size_bytes"],
                                content_id=att["content_id"],
                                is_inline=att["is_inline"],
                                sha256=att["sha256"],
                                saved_path=att["saved_path"],
                                created_at=None,
                            )
                        except Exception:
                            continue
                    total_inserted += 1
                except Exception:
                    continue
            conn.commit()
        finally:
            mbox.close()

    conn.close()
    print(f"SQLite: {db_path}  rows: {total_inserted}")


if __name__ == "__main__":
    main()
