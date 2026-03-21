# Phase 2.4 — Plan: Selective document-content extraction

**Goal:** Extract text content from a **subset** of high-value attachment types only (e.g. PDF, plain-text, and optionally Office), store it in a structured way, and make it available for search/analytics without redesigning the pipeline or adding OCR for images.

---

## 1. Scope (in)

- **Selective by type:** Only extract from attachment types that are:
  - High signal for business (cotización, factura, pedidos): **PDF**, **plain text** (`.txt`, `text/plain`), and optionally **Word** (`.doc`/`.docx`) and **Excel** (`.xls`/`.xlsx`) when lightweight extraction is available.
- **Metadata already present:** Reuse Phase 2.3 `attachments` table and `email_id`; add **additive** columns or a small companion table for extracted text (e.g. `extracted_text` or `attachment_text` table keyed by `attachment_id`).
- **Optional and off-by-default if expensive:** e.g. PDF text extraction can be opt-in or limited by size/count to keep runtimes and storage under control.
- **No OCR, no image parsing:** Phase 2.4 does **not** include OCR or image-to-text. Images remain metadata-only (filename, type, size, hash).

---

## 2. Scope (out)

- Full-text indexing of every attachment type.
- OCR or any image/scan content extraction.
- Changing ingestion flow for non-selected types.
- Mandatory re-import: extraction can be a **post-pass** over existing `attachments` rows (with payload re-read from mbox if needed) or a future optional step during import.

---

## 3. Proposed design (minimal)

1. **Storage**
   - Option A: Add `extracted_text TEXT` (or `content_preview TEXT`) to `attachments`; NULL when not extracted or not applicable.
   - Option B: New table `attachment_text(attachment_id, extracted_text, extracted_at)` to keep `attachments` unchanged and allow re-extraction without touching metadata.
   - Prefer **Option A** if schema change is acceptable (one place to query); otherwise Option B.

2. **Extraction triggers**
   - Only for rows where `content_type` / filename indicates:
     - `application/pdf` → PDF text extraction (e.g. PyMuPDF/fitz, or pdfminer).
     - `text/plain` or filename `*.txt` → decode payload (already available at ingest if we store it; else skip or do in post-pass from mbox).
     - Optionally: Office (docx/xlsx) via `python-docx` / `openpyxl` for text/sheet text only.
   - Skip: `image/*`, `message/delivery-status`, `multipart/report`, and any type not in the allow-list.
   - Optional guardrails: max size per attachment (e.g. 10 MB), max total extracted chars per email, or cap number of PDFs per run.

3. **When to run**
   - **Post-pass (recommended for v1):** Script that:
     - Reads attachment metadata from `attachments` (and optionally re-reads payload from mbox by matching message + part_index if payload not stored).
     - For each row in allow-list, runs the appropriate extractor, writes to `extracted_text` (or `attachment_text`).
   - Alternatively: during `02_mbox_to_sqlite.py` for selected types only, when payload is in memory (adds latency and dependency on extractors in the main pipeline).

4. **Reporting**
   - Add to summary/report only if present: e.g. “Attachments with extracted text: N”, “Sample of PDF-extracted snippets” (optional). No redesign of existing report; additive only.

5. **Dependencies**
   - PDF: `pymupdf` (fitz) or `pdfminer.six` (lighter).
   - Office: `python-docx`, `openpyxl` (optional).
   - No new system binaries required if using pure-Python or wheel-friendly libs.

---

## 4. Validation

- Counts: attachments eligible for extraction (by type) vs. rows with non-empty `extracted_text`.
- Spot-check: a few PDFs and plain-text attachments to ensure extracted text is readable and not corrupted.
- Ensure extraction failures do not remove or overwrite existing metadata.

---

## 5. Risks and mitigations

- **PDF complexity:** Some PDFs are scanned or image-only → extractor returns empty or garbage. Mitigation: treat as “no text”; do not retry with OCR in Phase 2.4.
- **Performance:** PDF extraction can be slow. Mitigation: post-pass with progress bar; optional limit (e.g. first N PDFs per run or per email).
- **Storage:** Extracted text can be large. Mitigation: optional truncation (e.g. first 50k chars per attachment); store in separate table if you want to avoid bloating `attachments`.

---

## 6. Suggested implementation order

1. **Schema:** Add `extracted_text TEXT` to `attachments` (or create `attachment_text`).
2. **Allow-list:** Define in code the set of `content_type` / filename patterns that trigger extraction.
3. **Extractors:** Implement PDF (and optionally plain-text from stored payload or mbox) in a small module (e.g. `extract_attachment_text.py` or under `parse_mbox`).
4. **Post-pass script:** `scripts/validation/extract_attachment_text.py` (or similar) that iterates `attachments`, runs extractors, updates DB. Progress bar and optional `--limit`.
5. **Report:** Add one line or a small block to the report when `attachments` has at least one non-null `extracted_text` (e.g. count, optional sample). No redesign.
6. **Docs:** Short `PHASE2_4_EXTRACTION.md` describing allow-list, storage, and how to run the post-pass.

---

## 7. Success criteria

- High-value attachment types (PDF, plain text; optionally Word/Excel) have a defined path to extracted text stored in the DB.
- Pipeline and existing report remain backward-compatible.
- No OCR or image extraction in scope.
- Clear separation: metadata (Phase 2.3) vs. optional text extraction (Phase 2.4).
