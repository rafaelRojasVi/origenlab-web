# Phase 2.3 — Attachments (metadata layer)

**Status: complete.** Orphan cleanup, validation, and report integration are in place.

**Goal:** Add a robust, backward-compatible attachment metadata layer on top of the existing email pipeline, without changing the PST → mbox → SQLite → JSONL/report flow or adding OCR/AI.

This phase treats attachments as a **second layer of business evidence** (quotes, invoices, datasheets, etc.), with:

- A normalized `attachments` table.
- Lightweight counters on `emails`.
- Extraction during ingestion.
- Validation tooling and minimal reporting hooks.

---

## 1. Migration and backfill strategy

- **Source of truth for attachments is raw MIME (mbox)**, not SQLite.
- Existing SQLite rows do **not** contain attachment payloads, so a fully correct attachment inventory requires re-reading MIME messages.

Therefore:

- The **primary safe path** for Phase 2.3 is **full re-import** from mbox:

  ```bash
  uv run python scripts/ingest/02_mbox_to_sqlite.py
  uv run python scripts/tools/dedupe_emails_by_message_id.py   # optional; enables FK and orphan cleanup
  ```

- This will:
  - Recreate the `emails` table.
  - Populate Phase 2.1 and 2.2 fields.
  - Populate the new `attachments` table and `emails.attachment_count` / `emails.has_attachments`.

- A separate “backfill directly from mbox for existing DB” script is **not** provided in this phase, because:
  - Matching messages between DB rows and raw mbox by position or ID is not guaranteed to be stable across historical runs.
  - A fragile, non-deterministic backfill would be worse than a clear, reproducible full import.

> **Conclusion:** For Phase 2.3, **full re-import** is the recommended and supported way to populate attachments.

---

## 2. Schema changes

### 2.1 `emails` table (additive columns)

- `attachment_count` INTEGER
- `has_attachments` INTEGER (0/1)

These are **derived fields**:

- During ingestion:
  - `attachment_count = number of attachment rows inserted for that email`.
  - `has_attachments = 1 if attachment_count > 0 else 0`.
- They can be validated against the `attachments` table (see validation script).

### 2.2 `attachments` table (new)

Created in `db.py`:

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `email_id` INTEGER NOT NULL  → FK to `emails.id` (ON DELETE CASCADE)
- `part_index` INTEGER NOT NULL (0-based ordinal among attachment-like parts)
- `filename` TEXT (decoded from MIME; may be NULL)
- `content_type` TEXT (e.g. `application/pdf`, `image/png`)
- `content_disposition` TEXT (raw header, e.g. `attachment; filename="..."`)
- `size_bytes` INTEGER (0 allowed)
- `content_id` TEXT (for inline/embedded parts)
- `is_inline` INTEGER (0/1; see classification rules below)
- `sha256` TEXT (content hash when payload available; NULL otherwise)
- `saved_path` TEXT (currently unused; reserved for optional raw file persistence)
- `created_at` TEXT (ISO timestamp; currently NULL in ingestion)

Indexes:

- `idx_attachments_email_id` on `(email_id)`
- `idx_attachments_sha256` on `(sha256)`

---

## 3. Attachment detection rules

Implemented in `parse_mbox.walk_attachments(msg: Message)`.

Rules (conservative, explicit):

- **Never** treat the main text/plain or text/html body parts as attachments:
  - Parts with `content_type` starting with `text/` and **no** `Content-Disposition: attachment` are skipped — they remain part of the body pipeline.

- **Treat as attachment if _any_ of:**
  - `Content-Disposition` contains `"attachment"`, OR
  - A `filename` is present (after MIME decoding), OR
  - `Content-Type` indicates common binary/document payloads, e.g.:
    - `application/pdf`
    - `application/msword`
    - `application/vnd.ms-excel`
    - `application/vnd.ms-powerpoint`
    - `application/vnd.openxmlformats-officedocument.*`
    - `application/vnd.ms-*`
    - `application/zip`, `application/x-zip-compressed`, `application/x-rar-compressed`

- **Treat as likely inline if:**
  - `Content-Disposition` contains `"inline"`, OR
  - `Content-ID` is present (embedded images, `cid:` references), OR
  - `Content-Type` starts with `image/` and was not already strongly flagged as attachment.

- Only parts that satisfy **attachment or inline signals** are recorded in `attachments`.  
  - For `is_inline`, the code reflects the best guess based on the above heuristics.

For each recorded part, we compute:

- `size_bytes` from the decoded payload length.
- `sha256` over the raw bytes, when available.

Errors while decoding or hashing **do not abort ingestion**; they just result in partial/empty metadata for that part.

---

## 4. Ingestion path (02_mbox_to_sqlite)

In `scripts/ingest/02_mbox_to_sqlite.py`:

- For each `msg` in each mbox:
  1. Bodies:
     - `body_content(msg)` for `body` / `body_html`.
     - `extract_body_structured(msg)` → Phase 2.1 fields.
     - `extract_full_and_top_reply(structured)` → Phase 2.2 fields.
  2. Attachments:
     - `attachments = walk_attachments(msg)` → list of metadata dicts.
  3. Insert email:

     ```python
     email_id = insert_email(
         conn,
         ...,
         full_body_clean=full_body_clean,
         top_reply_clean=top_reply_clean,
         attachment_count=len(attachments),
         has_attachments=bool(attachments),
     )
     ```

  4. Insert attachment rows:

     ```python
     for att in attachments:
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
     ```

- Any exception inserting a specific attachment is caught and ignored so that:
  - The email row is still kept.
  - Other attachments for the same email can still be recorded.

---

## 5. Validation tooling

Script: `scripts/validation/validate_attachments.py`

Run:

```bash
uv run python scripts/validation/validate_attachments.py
```

It reports:

- **Totals (audit):**
  - `Total emails` = `COUNT(*) FROM emails`
  - `Total attachments` = `COUNT(*) FROM attachments`
  - `Emails with attachments` = `COUNT(*) FROM emails WHERE has_attachments = 1`  
    (must be ≤ total emails; do **not** use `COUNT(DISTINCT email_id) FROM attachments`, which can exceed total emails after dedupe due to orphan attachment rows.)

- **Attachment reporting refinement:**
  - Emails with non-inline attachments; emails with business-document attachments.
  - Attachment counts by broad class: images, pdf, excel/csv, word, archives, delivery/report noise, other docs.
  - Top business-doc extensions; cotización emails with business-doc attachments (see §5.3 for heuristics).

- **Type breakdown:**
  - Top 15 `content_type` values.
  - Top 15 file extensions (derived from `filename`).
  - Inline vs non-inline (by `is_inline`).

- **Document-type counts:**
  - Emails with **PDF** attachments.
  - Emails with **Excel**-like attachments (xls/xlsx/csv).
  - Emails with **Word** docs (doc/docx).
  - Emails with **images** (`image/%`).

- **Consistency checks (`emails` vs `attachments`):**
  - `has_attachments = 1` but **no** attachment rows.
  - `attachment_count` not equal to actual number of `attachments` rows per email.

- **Diagnostics:**
  - Attachments with **no filename but `size_bytes > 0`**.
  - Attachments with `size_bytes = 0`.
  - Number of distinct `sha256` values that appear in **multiple** attachments (possible duplicates).

- **Samples (up to 5 each):**
  - PDF, Excel, Word, and image attachments:
    - Shows `email_id`, `filename`, `content_type`, `size_bytes`, and `subject`.

Use this to confirm:

- Attachment metadata is present.
- Counters on `emails` (`attachment_count`, `has_attachments`) match.
- PDFs / spreadsheets / Word documents / images look reasonable.

### 5.1 Validation findings (aggregate fix and extension fix)

**Impossible aggregate (resolved):**  
An earlier version of the script reported `total emails: 222,884` and `emails with attachments: 282,004`, which is impossible if both refer to the same dataset. The cause was:

- `emails_with_attachments` was computed as `COUNT(DISTINCT email_id) FROM attachments`.
- After running `dedupe_emails_by_message_id.py`, duplicate email rows are deleted from `emails`, but SQLite’s `PRAGMA foreign_keys` is not enabled in that script, so **attachment rows are not cascade-deleted** and many rows in `attachments` reference `email_id` values that no longer exist in `emails` (orphans).
- So `COUNT(DISTINCT email_id) FROM attachments` was counting distinct ids that include deleted emails, and could exceed `COUNT(*) FROM emails`.

**Fix:**  
`emails_with_attachments` is now defined as `COUNT(*) FROM emails WHERE has_attachments = 1`, so it is always ≤ total emails. The script also prints side-by-side counts and the number of **orphan attachment rows** (rows in `attachments` whose `email_id` is not in `emails`).

**Extension fix:**  
The “By extension” breakdown previously used a 3-argument `instr()` (invalid in SQLite) and then a nested expression that returned empty for single-dot filenames (e.g. `file.pdf`), producing a large “.” bucket. The script now derives the substring after the **last** dot via a `CASE` over nested `SUBSTR`/`INSTR`, so single-dot filenames get the correct extension (e.g. `.pdf`, `.jpg`) and the “.” bucket is removed.

**Corrected metrics (example after dedupe):**

- `COUNT(*) FROM emails`: 222,884  
- `COUNT(*) FROM attachments`: 873,224  
- `COUNT(*) FROM emails WHERE has_attachments = 1`: 110,520 (emails with attachments)  
- Orphan attachment rows (`email_id` not in `emails`): ~401k (expected after dedupe without FK cascade).

**Zero-byte attachments:**  
The script adds a “Zero-byte attachments” section: breakdown by `content_type`, by extension, by `is_inline`, sample filenames, and count among likely business docs (pdf/doc/xls/xlsx). Many zero-byte entries are inline or non-document types (e.g. delivery-status, rfc822-headers); the breakdown helps confirm whether they are mostly noise.

**Status:**  
Phase 2.3 is validated when: (1) `emails_with_attachments` ≤ total emails, (2) orphan attachment rows are 0 after dedupe, (3) consistency checks (has_attachments/attachment_count vs attachments table) show no drift. After the dedupe fix and report wiring, Phase 2.3 is **complete**.

### 5.2 Orphan attachment rows — root cause and dedupe fix

**Root cause:**  
When `dedupe_emails_by_message_id.py` deletes duplicate email rows, attachment rows that referenced the deleted `email_id` should be removed too. The schema defines `FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE`, but in SQLite **foreign key enforcement is off by default**. The dedupe script did not set `PRAGMA foreign_keys=ON`, so deletes from `emails` did **not** cascade into `attachments`. That left **orphan** attachment rows (rows whose `email_id` no longer exists in `emails`). Those orphans made `COUNT(DISTINCT email_id) FROM attachments` exceed `COUNT(*) FROM emails`.

**Dedupe cleanup fix:**  
The dedupe script was updated to:

1. **Enable foreign keys:** `PRAGMA foreign_keys=ON` so that when duplicate emails are deleted, their attachment rows are cascade-deleted.
2. **Explicit orphan cleanup (safeguard):** Before dedupe, run  
   `DELETE FROM attachments WHERE email_id NOT IN (SELECT id FROM emails)`  
   so any orphans left from a previous run (without FK) are removed.
3. **Order of operations:** Orphan cleanup first, then delete duplicate emails (CASCADE removes their attachments). The script is idempotent: a second run removes 0 duplicates and 0 orphans.
4. **Post-dedupe validation:** The script prints how many orphan attachment rows were removed and the final orphan count (expected 0 after the fix).

**Recommendation:** After a full re-import, run dedupe once; then run `validate_attachments.py` and confirm “Orphan attachment rows” is 0.

### 5.3 All attachments vs business-document attachments

Reporting distinguishes:

- **All attachments:** Every row in `attachments` (including inline images, delivery-status parts, multipart/report, etc.).
- **Business-document attachments:** A conservative subset used for “emails with business-doc attachments” and “top business-doc extensions” in validation and reporting.

**Business-doc heuristics (included):**

- PDF (`application/pdf` or filename `*.pdf`).
- Word (`*.doc`, `*.docx`, or content-type msword/wordprocessing).
- Excel/CSV (`*.xls`, `*.xlsx`, `*.csv`, or spreadsheet/ms-excel content-type).
- Archives (`*.zip`, `*.rar`, or zip/x-zip/rar content-type).
- XML (filename `*.xml` or `application/xml` / `text/xml`).

**Excluded from business-doc bucket:**

- `image/*` (inline or not — not treated as business documents).
- Noise types: `message/delivery-status`, `multipart/report`, `text/rfc822-headers`.
- Multipart container-only artifacts (no separate “business-doc” flag for container parts).

The validation script reports: total emails with attachments, emails with **non-inline** attachments, emails with **business-doc** attachments, attachment counts by broad class (images, pdf, excel/csv, word, archives, delivery/report noise, other), top business-doc extensions, and (if easy) cotización emails with business-doc attachments.

---

## 6. Report integration (complete)

`scripts/reports/generate_client_report.py` includes Phase 2.3 attachment metrics when the `attachments` table exists.

**Summary JSON (`summary.json`)** — key `attachments` (object or `null` if no table):

- `emails_with_attachments`: `COUNT(*) FROM emails WHERE has_attachments = 1`
- `emails_with_non_inline_attachments`: distinct emails with at least one non-inline attachment row (existing emails only)
- `emails_with_business_doc_attachments`: distinct emails with at least one business-doc attachment (see §5.3)
- `attachment_counts_by_broad_class`: `{ images, pdf, excel_csv, word, archives, delivery_report_noise, other_docs }` (counts of attachment rows by class, existing emails only)
- `top_business_doc_extensions`: list of `{ "ext", "count" }` (top 10)
- `cotizacion_emails_with_business_doc_attachments`: distinct emails that have a business-doc attachment and subject/top_reply_clean containing “cotización”/“cotizacion”

**HTML (`index.html`)** — compact “Adjuntos — resumen (Phase 2.3)” section:

- Emails con adjuntos; con adjuntos no inline; con adjuntos business-doc; cotización + business-doc
- One-line counts by broad class (imágenes, PDF, Excel/CSV, Word, archivos, delivery/report, otros)
- Table: top business-doc extensions and counts

Existing sections and semantics remain unchanged; reports that do not use attachment data are unaffected.

---

## 7. Scope and limitations

- **In scope (Phase 2.3):**
  - Attachment **metadata**:
    - type, size, filename, hashes.
  - Normalized `attachments` table.
  - Validation tooling.
  - Minimal reporting.

- **Out of scope (for now):**
  - OCR or text extraction from PDFs/images.
  - Full content indexing of attachments.
  - Any ML/AI or semantic interpretation of attachment content.

If/when attachment text extraction is added in a later phase, it should:

- Be clearly optional.
- Use existing `attachments` metadata as input.
- Keep raw metadata intact for reproducibility.

