# Phase 2.4 — Selective attachment content extraction (no OCR)

Status: complete.

## Goal
Add an **optional post-pass** that extracts lightweight text/structure from **high-value business attachments** so we can:
- classify document intent (cotización / factura / OC / lista de precios / ficha técnica)
- enrich the client report with **document-level** signals

This phase is intentionally conservative:
- **No OCR** (image-only/scanned PDFs remain empty)
- no LLMs, no RAG, no vector DB
- best-effort extraction with explicit `success/empty/skipped/failed/unsupported` states

## What’s new (schema)
New table: `attachment_extracts`
- Linked to `attachments.id` via `attachment_id` (unique) with `ON DELETE CASCADE`.
- Stores truncated text + counts + rule-based doc type + boolean signals.

Key fields:
- `extract_status`: `success | empty | skipped | failed | unsupported`
- `extract_method`: `pdf_text | docx | xlsx | csv | xml | none`
- `text_preview`: short excerpt (for sampling/report)
- `text_truncated`: truncated content (bounded)
- `char_count`, `page_count`, `sheet_count`
- `detected_doc_type`: `quote | invoice | price_list | purchase_order | datasheet | unknown`
- `has_quote_terms`, `has_invoice_terms`, `has_price_list_terms`, `has_purchase_terms`
- `error_message`, `created_at`

## Extraction logic
Implemented in `src/origenlab_email_pipeline/attachment_extract.py`.

Supported types:
- **PDF**: text extraction via PyMuPDF (no OCR)
- **DOCX**: paragraph text via `python-docx`
- **XLSX**: sheet names + small cell sample via `openpyxl` (read-only)
- **CSV**: reads a safe row sample via Python `csv`
- **XML** (optional but enabled): parse + gather text nodes (capped)

Truncation policy:
- Always normalizes whitespace.
- Stores `text_preview` (first ~1.6k chars) and `text_truncated` (first ~50k chars).

## Processing workflow (post-pass)
Script: `scripts/validation/extract_attachment_text.py`

How it works:
- Reads existing `attachments` + `emails` rows.
- Uses `emails.source_file` (mbox path) and `emails.message_id` to re-open the original mbox and locate the email message.
- Walks MIME parts, computes `sha256(payload)` and matches to `attachments.sha256` (preferred).
- Fallback match: `part_index` when sha256 isn’t available.
- Writes/upserts one row per attachment into `attachment_extracts`.

Candidate selection (conservative):
- `is_inline = 0`
- `size_bytes > 0`
- skips images + delivery/report noise types
- only supported methods (pdf/docx/xlsx/csv/xml)

### Important prerequisite
This requires access to the original mbox files referenced by `emails.source_file`.

If the mbox tree moved, extraction will mark rows as skipped with an error.

## Validation
Script: `scripts/validation/validate_phase2_4_extracts.py`

Outputs:
- totals (emails/attachments/extract rows)
- counts by `extract_status` and `extract_method`
- doc type distribution (success only)
- boolean signal counts
- samples of `text_preview` per method/type
- top error messages for `failed/skipped`

## Report integration
`scripts/reports/generate_client_report.py` now adds:
- `summary["attachment_extracts"]` (or null if table missing)

And renders a compact HTML card:
- “Adjuntos — contenido extraído (Phase 2.4)”
- totals + status counts + method counts + top detected doc types

## How to run (typical order)

1) Run Phase 2.4 extraction (post-pass):

```bash
cd apps/email-pipeline   # from OrigenLab monorepo root
uv run python scripts/validation/extract_attachment_text.py
```

Optional flags:
- `--limit N` to test on a small subset
- `--only pdf_text|docx|xlsx|csv|xml` to focus one method
- `--force` to delete and re-extract

2) Validate:

```bash
uv run python scripts/validation/validate_phase2_4_extracts.py
```

3) Regenerate client report:

```bash
uv run python scripts/reports/generate_client_report.py
```

## Limitations (known / intentional)
- **No OCR**: scanned PDFs/images will be `empty`.
- Matching depends on `emails.message_id` and stable access to the mbox files.
- Extraction is truncated by design; this is for signal/typing, not archiving full documents.

