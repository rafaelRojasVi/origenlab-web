# Phase 2.1 — Better body extraction

**Status:** Implemented.

**Goal:** Improve message body extraction so downstream phases can rely on stronger structured text and metadata, while preserving backward compatibility with existing reports.

---

## Summary of changes

1. **Parser (`parse_mbox.py`)**
   - **`html_to_text_improved(html)`** — Improved HTML→plain: removes `<script>` and `<style>` contents, preserves line breaks from `<br>`, `</p>`, `</div>`, `</tr>`, `</li>`, `<hr>`, then strips remaining tags, decodes entities, normalizes whitespace.
   - **`_normalize_whitespace(text)`** — Collapses spaces/tabs, preserves single newlines, collapses multiple blank lines (used for plain-text cleaning).
   - **`extract_body_structured(msg)`** — Returns a dict with:
     - `body_text_raw` — Primary extracted text in backward-compatible style (plain if present, else legacy `html_to_text` on HTML).
     - `body_text_clean` — Best readable text: normalized plain or improved HTML cleaning when source is HTML.
     - `body_source_type` — `"plain"` | `"html"` | `"mixed"` | `"empty"`.
     - `body_has_plain` — True if any `text/plain` part was found.
     - `body_has_html` — True if any `text/html` part was found.
   - **`body_content(msg)`** and **`body_text(msg)`** are unchanged; existing callers keep the same behaviour.

2. **Schema (`db.py`)**
   - New columns on `emails` (additive; existing DBs get them via `init_schema`):
     - `body_text_raw` (TEXT)
     - `body_text_clean` (TEXT)
     - `body_source_type` (TEXT)
     - `body_has_plain` (INTEGER, 0/1)
     - `body_has_html` (INTEGER, 0/1)
   - **`insert_email`** accepts optional kwargs for these; existing callers can omit them (columns stay NULL or empty).

3. **Ingestion (`02_mbox_to_sqlite.py`)**
   - For each message, calls `body_content(msg)` (unchanged) for `body` and `body_html`, and **`extract_body_structured(msg)`** for the new fields, then passes all to `insert_email`.

---

## Extraction fields reference

| Field               | Type   | Meaning |
|---------------------|--------|--------|
| `body`              | TEXT   | Unchanged: best plain text (plain parts, or HTML stripped with legacy `html_to_text`). |
| `body_html`         | TEXT   | Unchanged: concatenated raw HTML parts. |
| `body_text_raw`     | TEXT   | Same logic as current `body` for compatibility; primary extracted text before improved cleaning. |
| `body_text_clean`   | TEXT   | Best readable: normalized plain or **improved** HTML cleaning when source is HTML. Prefer this for analytics/search. |
| `body_source_type`  | TEXT   | `plain` \| `html` \| `mixed` \| `empty`. |
| `body_has_plain`    | INTEGER| 1 if message had at least one `text/plain` part, else 0. |
| `body_has_html`     | INTEGER| 1 if message had at least one `text/html` part, else 0. |

---

## Backward compatibility

- **Reports** that only use `body` and `body_html` are unchanged; both columns are still populated by `body_content()`.
- **New code** can use `body_text_clean` for better HTML-only readability and `body_source_type` / `body_has_plain` / `body_has_html` for filtering or analytics.

---

## How to run

- **Ingestion:** Run as before. New DBs get the full schema; existing DBs get new columns added on first `init_schema()` (e.g. when running `02_mbox_to_sqlite.py`).
  ```bash
  uv run python scripts/ingest/02_mbox_to_sqlite.py
  ```
- **Tests:**
  ```bash
  uv run pytest tests/test_parse_mbox_body.py -v
  ```

---

## Tests

- `test_body_content_plain_only` / `test_body_content_html_only` / `test_body_content_multipart_prefers_plain` — Backward compatibility of `body_content`.
- `test_extract_plain_only` / `test_extract_html_only` / `test_extract_multipart_both` — Source type and raw/clean for plain, HTML, mixed.
- `test_extract_empty_or_attachment_only` — No body → `empty`, has_plain/has_html False.
- `test_extract_html_with_scripts_and_styles` — Script/style removed; visible content in `body_text_clean`.
- `test_extract_broken_charset_decoding` — `decode_payload` fallback for invalid bytes.

---

## What comes next (2.2)

- **Quote and signature handling:** Derive `full_body_clean` and `top_reply_clean` from `body_text_clean` (or `body`); strip reply chains and signature blocks; add tests and `docs/PHASE2_QUOTES_SIGNATURES.md`.
