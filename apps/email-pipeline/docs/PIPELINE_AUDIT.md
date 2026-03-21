# Pipeline audit — OrigenLab email intelligence

**Date:** 2026-03-15  
**Scope:** Current codebase as of Phase 1. No code changes; inspection only.

---

## 1. Current ingestion flow (PST → mbox → SQLite)

### 1.1 PST → mbox

- **Script:** `scripts/ingest/01_convert_pst.sh` (Bash).
- **Tool:** `readpst` (pst-utils). Options: `-o <outdir> -r -D -j 4` (fallback without `-j`).
- **Paths:** `ORIGENLAB_RAW_PST_DIR` or `$ORIGENLAB_DATA_ROOT/raw_pst` → `ORIGENLAB_MBOX_DIR` or `$ROOT/mbox`.
- **Behaviour:** Finds all `*.pst` / `*.PST` under input dir; each PST gets a subdir under mbox named by basename (e.g. `backup.pst` → `mbox/backup/`). No incremental option; re-run overwrites.
- **Output:** One or more mbox-like files per PST folder (readpst layout; files may have no extension or `.mbox`).

### 1.2 mbox → SQLite

- **Script:** `scripts/ingest/02_mbox_to_sqlite.py`.
- **Behaviour:**
  - Discovers files under `resolved_mbox_dir()` via `rglob("*")` and `is_probably_mbox(path)` (extension `.mbox`/empty or content starts with `From `).
  - **Replaces entire table:** `init_schema(conn)` then `conn.execute("DELETE FROM emails")` then inserts from every mbox file.
  - For each message: reads `Message-ID`, `Subject`, `From`, `To`/`Cc`/`Bcc`, `Date`, body via `parse_mbox.body_content(msg)`.
  - Inserts one row per message; commits per mbox file.
- **No incremental load:** Always full replace. No checkpointing or “since last run.”

---

## 2. Existing schema

**Source:** `src/origenlab_email_pipeline/db.py`

```sql
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    folder TEXT,
    message_id TEXT,
    subject TEXT,
    sender TEXT,
    recipients TEXT,
    date_raw TEXT,
    date_iso TEXT,
    body TEXT,
    body_html TEXT
);
CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id);
CREATE INDEX IF NOT EXISTS idx_emails_date_iso ON emails(date_iso);
```

- **Optional migration:** `ALTER TABLE emails ADD COLUMN body_html TEXT` (ignored if already present).
- **No other tables:** No attachments, threads, entities, or marts. Single-table design.

---

## 3. Current parsing logic for body extraction

**Source:** `src/origenlab_email_pipeline/parse_mbox.py`

### 3.1 Decoding

- `decode_payload(raw, charset)`: decodes bytes with given charset; falls back to `utf-8` with `errors="replace"`. Handles `ascii`/`us-ascii` as UTF-8.

### 3.2 HTML → text

- `html_to_text(html)`: regex-based, no external deps. Removes `<script>`, `<style>`, comments; strips tags; unescapes entities; normalizes whitespace and blank lines. No preservation of structure (e.g. list items).

### 3.3 Part walking

- `_walk_parts(msg)`: walks MIME parts; skips parts with `Content-Disposition: attachment`. Collects `text/plain` and `text/html` payloads (decoded). Returns `(plain_parts, html_parts)`.

### 3.4 Body choice

- `body_content(msg)` returns `(body, body_html)`:
  - **body:** Concatenation of plain parts; if none, uses `html_to_text(html_parts)`.
  - **body_html:** Concatenation of raw HTML parts (empty if none).
- No storage of “source type” (plain vs html vs mixed). No `top_reply` or quote/signature stripping. No attachment metadata extraction.

### 3.5 Other headers

- `recipients_header(msg)`: concatenates To, Cc, Bcc with `"; "`.
- `date_iso_from_msg(msg)`: parses `Date` via `email.utils.parsedate_to_datetime`, returns ISO string or `None`.

---

## 4. Dedupe logic

**Script:** `scripts/tools/dedupe_emails_by_message_id.py`

- **Rule:** Keep one row per `message_id`. `DELETE FROM emails WHERE id NOT IN (SELECT MIN(id) FROM emails GROUP BY COALESCE(message_id, id))`.
- **Effect:** Same Message-ID in multiple PSTs → one row kept (lowest `id`). Rows with NULL `message_id` are kept as-is (each has its own `id` in GROUP BY).
- **Connection:** `timeout=60` to wait for lock.
- **No near-duplicate logic:** No subject/sender/date/body-hash grouping. No “possible_duplicate_group” or diagnostics table.

---

## 5. Current keyword rules / business filters

### 5.1 Business filter (Python)

**Sources:** `src/origenlab_email_pipeline/business_filter_rules.py`, `email_business_filters.py`

- **Categories (precedence order):** bounce_ndr, spam_suspect, social_notification, newsletter, logistics, marketplace, institution, internal, supplier, customer, business_core, unknown.
- **Rules:** Domain lists (INTERNAL_DOMAINS, LOGISTICS_DOMAINS, INSTITUTION_DOMAINS, etc.) and substring patterns (BOUNCE_*, NEWSLETTER_*, BUSINESS_CORE_PATTERNS, COMMERCIAL_SUBTYPE_PATTERNS). All hardcoded in Python; no YAML/config.
- **Classification:** `classify_email(sender, recipients, subject, body)` → tags, primary_category, sender_domain, rollup flags (is_business_only_candidate, is_noise, is_operational, etc.). Optional commercial_subtype (quote/order/invoice/support/followup) when primary is business_core.
- **Views:** all_messages, operational_no_ndr, business_only, business_only_external. Implemented as predicates over classification.
- **Batch:** `run_filter_pass(db_path, limit, top_n, sample_size)` streams rows from `emails`, classifies each, aggregates counts and per-view domain counts, and collects a business_only sample. No persisted classification; recomputed every run.

### 5.2 Client report aggregates (SQL)

**Source:** `scripts/reports/generate_client_report.py` — `_merged_aggregate_sql()`, etc.

- **Separate logic from business filter:** Same concepts (cotización, universidad, bounce-like, equipment) implemented again as SQL `LIKE` on `LOWER(COALESCE(subject,'') || ' ' || COALESCE(body,''))`.
- **Keywords:** cotiz%, proveedor, factura/invoice, pedido/purchase order/orden de compra/oc, universidad + list of .cl universities + .edu, mailer-daemon/postmaster/delivery status/undeliverable, and equipment terms (microscop%, centrifug%, balanza, cromatograf/hplc, etc.). Cross terms: cotiz + equipment.
- **Effect:** Duplication between Python rules and SQL; equipment list and intent patterns exist in two places. No single config or catalog.

---

## 6. Current report-generation flow

### 6.1 generate_client_report.py

- **Input:** DB path, optional `--out`, `--fast`, `--with-business-filter`, `--embeddings-sample`, `--domain-sample`, etc.
- **Steps:**
  1. **Phase 1 — SQL:** One full-table scan with `_merged_aggregate_sql()` (totals, with_date, with_body, keyword and equipment counts, cotiz∧equipment). Optional second scan for by-year and by-year cotización.
  2. **Phase 2 — Optional embeddings:** If `--embeddings-sample > 0`, sample rows, encode with sentence-transformers (MiniLM), cluster (e.g. AgglomerativeClustering), write `clusters.json` and cluster summary for HTML.
  3. **Phase 3 — Domains:** Unless `--fast`, streams all rows (or a sample if `--domain-sample`), extracts sender/recipient domains, aggregates top sender/recipient domains (all and operational, external recipients). Can use multiprocessing workers.
  4. **Optional business filter:** If `--with-business-filter`, calls `run_filter_pass()` and writes business_filter_summary.json, business_only_sample.json, category_counts.csv, sender_domain_by_view.csv into the same output dir.
- **Outputs:** summary.json, index.html (Chart.js + embedded data), ALCANCE_INFORME.md (from docs/REPORT_SCOPE_CLIENT.md if present), optional clusters.json.

### 6.2 generate_business_filter_report.py

- Single call to `run_filter_pass(db_path, limit, top_n, sample_size)`; writes business_filter_summary.json, business_only_sample.json, category_counts.csv, sender_domain_by_view.csv to `--out` or default reports dir.

### 6.3 export_unique_emails_csv.py

- Single pass over `emails`: regex-extract addresses from `sender` and `recipients`, count as sender and in recipients, dedupe by address, write CSV (email, domain, count_as_sender, count_in_recipients, total_occurrences).

### 6.4 run_all_reports.py

- Orchestrator: runs export_unique_emails_csv (→ unique_emails.csv), then generate_client_report with `--with-business-filter` (and optional `--embeddings`). All into one output dir. Optional `--dedupe` runs dedupe script first.

### 6.5 03_sqlite_to_jsonl.py

- Exports full `emails` table to JSONL via `export_jsonl()` (orjson, one JSON object per line). Not part of the “report” pack; used for downstream/ML.

---

## 7. Current outputs (HTML / JSON / CSV)

| Output | Producer | Description |
|--------|----------|-------------|
| index.html | generate_client_report | Single-page dashboard: volume by year, cotización by year, classification/equipment charts, top sender/recipient domains, contrapartes (Para/Cc), exact senders, business filter section, optional embeddings cluster table. Chart.js CDN. |
| summary.json | generate_client_report | Aggregates, by_year, by_year_cotizacion, top_sender_domains, top_recipient_domains, top_senders_raw, cross_cotiz_equipo, classification/equipment tables, optional cluster_summary, optional business_filter embed. |
| ALCANCE_INFORME.md | generate_client_report | Scope/caveats (copied from docs/REPORT_SCOPE_CLIENT.md). |
| clusters.json | generate_client_report | Only if --embeddings-sample > 0: model, device, n_sample, n_clusters, clusters { id: [{subject, sender}, ...] }. |
| business_filter_summary.json | generate_business_filter_report or client report | total_classified, primary_category_counts, rollup_counts, view_counts, top_sender_domains_* per view, top_senders_business_only. |
| business_only_sample.json | same | List of sample rows (id, sender, subject, primary_category, tags). |
| category_counts.csv | same | category, count (one row per primary category). |
| sender_domain_by_view.csv | same | view, domain, count. |
| unique_emails.csv | export_unique_emails_csv | email, domain, count_as_sender, count_in_recipients, total_occurrences. |
| emails.jsonl | 03_sqlite_to_jsonl | One JSON per email row (id, source_file, folder, message_id, subject, sender, recipients, date_*, body, body_html). |

---

## 8. Gaps / weaknesses / technical debt

### 8.1 Ingestion and schema

- **Full replace only:** No incremental PST/mbox load; no idempotent “append new” or “merge by message_id.”
- **No attachment metadata:** Attachments are skipped in body extraction; no table or fields for filenames, MIME type, size.
- **No thread model:** In-Reply-To / References not stored; no thread_id or thread aggregation.
- **Single table:** No dimension tables (domains, addresses, organizations); no analytical marts.

### 8.2 Body and parsing

- **No source type:** Not stored whether body came from plain, HTML, or mixed.
- **No quote/signature stripping:** No `top_reply_clean` or similar; no separate full vs first-reply storage.
- **HTML cleaning is minimal:** Good for search, but no configurable rules or structure preservation.
- **Recipients as single string:** To/Cc/Bcc concatenated; no per-recipient rows or normalized addresses.

### 8.3 Deduplication

- **Only Message-ID:** No near-duplicate detection (same subject/sender/date/body hash). No diagnostics table for “possible duplicates.”

### 8.4 Rules and configuration

- **Hardcoded rules:** Domain lists and keyword patterns in Python. No YAML/JSON config or domain→org/sector mapping files.
- **Dual implementation:** Client report SQL duplicates business-filter and equipment concepts; no single equipment catalog or intent taxonomy shared by SQL and Python.

### 8.5 Classification and entities

- **Not persisted:** Classification is computed on the fly in report and filter pass; not stored in DB. No message-level tags or intent column.
- **No entity layer:** No dim_domain, dim_email_address, or organization/sector tables. No canonical client or “company” id.
- **Equipment:** Flat keyword list in two places; no equipment_catalog with aliases or brand/model extraction in the main pipeline.

### 8.6 Analytics and dashboard

- **No marts:** No mart_client_summary, mart_yearly_activity, mart_equipment_by_sector, etc. All aggregations recomputed from raw table.
- **No Streamlit (or other) app:** Only static HTML + JSON/CSV. No interactive filters or “explore by client/equipment/year.”
- **Recency/frequency:** Not precomputed (e.g. days_since_last_contact, messages_last_30d, active/inactive).

### 8.7 Commercial and caveats

- **No document signals table:** Quote/invoice/OC numbers and tracking IDs not extracted or stored as first-class signals.
- **Caveats in docs only:** ALCANCE and REPORT_SCOPE explain “mentions not sales”; UI could surface this more prominently and consistently.

### 8.8 Code quality

- **Tests:** Only `tests/test_email_business_filters.py` for classification. No tests for parse_mbox body extraction, dedupe, or report SQL.
- **Config:** Paths via env/pydantic only; no config file for rules or catalogs.
- **Incremental:** No notion of “last run” or incremental refresh for marts or reports.

---

## Summary

The pipeline is a **single-table SQLite + script-based reports** design: PST → mbox → SQLite (full replace), Message-ID dedupe, then SQL aggregates and Python business-filter pass producing HTML/JSON/CSV. Body extraction is plain-first with HTML fallback and simple cleaning; no attachments, threads, or entity layer. Rules are hardcoded and partly duplicated between SQL and Python. There are no analytical marts, no config-driven catalogs, and no interactive dashboard—only static report artifacts. The audit above is the basis for the extension plan (Phase 2–7).
