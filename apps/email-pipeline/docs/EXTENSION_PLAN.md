# Extension plan — multi-stage analytics pipeline and dashboard

**Purpose:** Turn the current email report pipeline into a proper multi-stage analytics system for OrigenLab: better extraction, normalized entities, analytical marts, and a Streamlit dashboard—with ML only where it adds value and strict caveats (mentions vs sales).

**Principle:** Prioritize extraction, cleaning, canonicalization, and marts before adding ML. One phase at a time, small commits.

**Reference:** [PIPELINE_AUDIT.md](./PIPELINE_AUDIT.md) for current state, gaps, and technical debt.

---

## Phase 1 — Audit (done)

- **Deliverables:** `docs/PIPELINE_AUDIT.md`, `docs/EXTENSION_PLAN.md`.
- **Status:** Complete. No code changes.

---

## Phase 2 — Improve extraction quality

**Goal:** Robust body pipeline, optional quote/signature stripping, attachment metadata, better dedupe diagnostics, thread reconstruction. All with tests.

**Audit gaps addressed:** Body source type and cleaning (8.2), attachment metadata (8.1), near-dup diagnostics (8.3), thread model (8.1).

### 2.1 Body extraction

- Prefer `text/plain` when present and usable; fallback to HTML→cleaned text.
- Add HTML cleaning: remove script/style, normalize whitespace, preserve meaningful line breaks.
- Persist: `body_text_clean`, optional `body_text_raw`, `body_source_type` (plain/html/mixed). Keep existing `body`/`body_html` during transition (e.g. add columns or new table).
- **Tests:** Unit tests for `body_content` / new extractor: plain-only, html-only, multipart, encoding edge cases.

### 2.2 Quote and signature handling

- Optional stripping of quoted reply blocks and signature blocks.
- Store: `full_body_clean`, `top_reply_clean`. Do not overwrite original extracted text.
- **Tests:** Messages with “On … wrote:”, “——” signature, multiple replies; assert top_reply vs full.

### 2.3 Attachment metadata

- Extract from MIME: filename, extension, MIME type, size (if available).
- New table: e.g. `attachments(message_id, filename, mime_type, size_bytes)` linked to emails (by message_id or id).
- **Tests:** Multipart with attachments; assert rows and metadata.

### 2.4 Better dedupe

- Keep Message-ID dedupe as primary.
- Add diagnostics: normalized subject, sender, recipients, date bucket, body hash. Build “possible_duplicate_group” or similar analysis table; do not auto-delete near-duplicates.
- **Tests:** Insert known near-dupes; assert grouping and that no row is removed without explicit policy.

### 2.5 Thread reconstruction

- Use headers: Message-ID, In-Reply-To, References.
- Fallback: normalized subject, participants, date proximity.
- New table: e.g. `threads(thread_id, first_message_at, last_message_at, message_count, participants_count)` and link messages to thread_id (e.g. `emails.thread_id`). Optional: dominant tags, dominant equipment per thread (computed view or mart).
- **Tests:** Simple chain (A→B→C); assert thread_id and counts.

**Phase 2 deliverables:** Schema changes (or migration script), updated parse_mbox (or new module), attachment/thread tables, dedupe-diagnostics script/table, tests, short doc (e.g. in docs/) on new fields and tables.

---

## Phase 3 — Normalization / entity layer

**Goal:** Canonical identities (email, domain, org), sector classification, message-intent tags, equipment catalog, brand/model extraction, commercial-document signals. Config-driven where possible.

**Audit gaps addressed:** No entity layer (8.5), hardcoded rules (8.4), no equipment catalog (8.5), no document signals (8.7).

### 3.1 Email identities

- Normalize: lowercase, trim, basic canonicalization. Optionally split display name vs address.
- Dimensions: e.g. `dim_email_address`, optionally `dim_domain`. Link emails to these (e.g. sender_id, recipient rows in a junction table if needed for analytics).

### 3.2 Company / organization

- Heuristic domain → organization name; collapse variants; mark internal domains.
- Config: `config/domain_org_map.yaml`, `config/internal_domains.yaml` (or similar). Allow overrides.

### 3.3 Sector classification

- Map domains/organizations to: internal, university/education, supplier, customer, government, logistics, marketplace, social/newsletter, bounce_ndr, spam_suspect, unknown.
- Rule-based first; configurable via YAML. Align with existing business_filter categories where it makes sense.

### 3.4 Message intent

- Tags: cotizacion, factura, pedido_oc, proveedor, logistica_envio, soporte, newsletter, social_notification, bounce_ndr, unknown. Rule-based patterns; store confidence and matched rule(s). Persist on message or in a classification table.

### 3.5 Equipment extraction

- Controlled vocabulary + aliases (balanza, pipeta, centrifuga, hplc_cromatografia, etc.). Config: `config/equipment_catalog.yaml`.
- Store: equipment_id, canonical_name, alias_matched, match_source (subject/body/attachment), count or boolean. Link to message (e.g. message_equipment junction).

### 3.6 Brand and model extraction

- Curated regex/patterns for Ohaus, IKA, Hielscher, etc. Store: brand, model_name, matched_text, confidence, message_id. Clearly label as “mentions” not sales.
- **Tests:** Sample emails with known brands/models; assert extraction and no overclaim.

### 3.7 Commercial document signals

- Extract probable quote numbers, invoice numbers, OC/PO numbers, tracking numbers, tender IDs. Store as weak signals with provenance (e.g. table or JSON column). Do not infer “sold”; use only as signals for dashboard and funnel proxy.

**Phase 3 deliverables:** Config files (domain_org, internal_domains, equipment_catalog, sector rules, intent rules), dimension/classification tables or columns, extraction scripts/modules, tests, doc (DATA_MODEL or similar).

---

## Phase 4 — Analytical marts

**Goal:** Stable derived tables for dashboard and reporting: message overview, yearly activity, client summary, client×year, recency/frequency, equipment summaries, sector/equipment/institution, brand-model, quote/invoice/PO-like, thread summary, data quality.

**Audit gaps addressed:** No marts (8.6), no precomputed recency/frequency (8.6).

### 4.1 Mart definitions (from spec)

- **mart_message_overview** — High-level message counts and coverage.
- **mart_yearly_activity** — Activity by year (and optionally month).
- **mart_client_summary** — Per client (domain or org): first_seen_at, last_seen_at, total_messages, sent_to_count, received_from_count, active_years, dominant_sector, dominant_equipment, cotizacion_message_count, invoice_like_count, po_like_count, ndr_count, newsletter_count.
- **mart_client_year** — Client × year breakdown.
- **mart_client_recency_frequency** — days_since_last_contact, messages_last_30d/90d/365d, active/inactive, reactivation_candidate.
- **mart_client_equipment_year** — Client × equipment × year (e.g. mention counts).
- **mart_sector_summary** — Sector-level aggregates.
- **mart_equipment_summary** — Equipment-level totals.
- **mart_equipment_year** — Equipment × year.
- **mart_equipment_by_sector** — Equipment × sector.
- **mart_equipment_by_institution** — Equipment × institution (e.g. university).
- **mart_brand_model_summary** — Brand/model mention counts.
- **mart_quote_like_summary**, **mart_invoice_like_summary**, **mart_po_like_summary** — Counts/signals from Phase 3.7.
- **mart_thread_summary** — Thread-level stats.
- **mart_data_quality** — % with body, % with date, NDR share, duplicate diagnostics, extraction coverage.

### 4.2 Implementation

- Clean SQL or Python transforms; idempotent and reproducible. Run after entity layer (Phase 3) is in place. Prefer incremental refresh where feasible (e.g. by max date).

**Phase 4 deliverables:** Mart table definitions (in schema or migrations), transform scripts or SQL, docs (e.g. DATA_MODEL.md) describing marts and refresh order.

---

## Phase 5 — Dashboard

**Goal:** Streamlit app for a non-technical business user: Spanish-friendly, filterable, with clear caveats; default to operational_no_ndr; optional switch to all_messages / business_only.

### 5.1 Pages (from spec)

1. **Resumen general** — Totals, date coverage, external contacts, business vs logistics vs newsletter vs NDR, activity by year.
2. **Clientes / contrapartes** — Top clients, frequent vs dormant, first/last seen, sector, activity trend.
3. **Equipos / productos** — Top equipment, by year, by sector, by institution, by client.
4. **Señales comerciales** — Cotización-like, factura-like, pedido/OC-like, funnel proxy; strong caveat: signals, not confirmed sales.
5. **Marcas y modelos** — Top brand/model mentions, examples.
6. **Explorar correos** — Search by company/domain/equipment/brand/year/tag; example threads/messages.
7. **Calidad de datos** — % with body/date, NDR share, duplicate diagnostics, extraction coverage.

### 5.2 Tech and UX

- Plotly for charts; tables downloadable (CSV). Config or env for DB path. Document in README_DASHBOARD.md.

**Phase 5 deliverables:** Streamlit app (e.g. `dashboard/` or `streamlit_app.py`), README_DASHBOARD.md, optional docker or run instructions.

---

## Phase 6 — ML / advanced analysis (only after Phases 2–5)

**Goal:** Add ML only where it clearly helps: topic clustering, semantic search, message-type classifier (from weak labels), organization similarity, near-duplicate detection. No sales prediction or “top sold” from email text.

### 6.1 Allowed ML

- Embedding-based topic clustering (e.g. on business-only messages).
- Semantic search over body/subject.
- Message-type classifier trained from rule-generated weak labels (cotizacion, factura, logistica, newsletter, etc.).
- Organization similarity / grouping to help merge company variants.
- Near-duplicate detection (embeddings or text similarity) for templated/repeated mail.

### 6.2 Out of scope

- Sales prediction; “top sold products” from email; any claim that a mention equals a purchase.

**Phase 6 deliverables:** Scripts or modules for clustering, search, classifier training/inference, similarity; integration points with marts or dashboard; doc (e.g. ML_SCOPE.md) stating what is and is not inferred.

---

## Phase 7 — Code quality and deliverables

**Goal:** Modular package, typed Python, CLI entrypoints, tests for parsers and entity extraction, reproducible outputs, config-driven rules, clear docs and caveats.

### 7.1 Engineering

- Package layout: keep `src/origenlab_email_pipeline/`; add or split modules for extraction, entities, marts, dashboard. CLI entrypoints (e.g. `python -m origenlab_email_pipeline.cli ingest`, `build_marts`, `run_dashboard`).
- Tests: parsers (body, attachments, threads), entity extraction, dedupe diagnostics, marts (smoke or snapshot). Typing where reasonable.

### 7.2 Documentation

- **README_ANALYTICS.md** — What the pipeline produces (marts, reports, caveats).
- **README_DASHBOARD.md** — How to run and use the Streamlit app.
- **docs/DATA_MODEL.md** — Tables, dimensions, marts, refresh order.
- **docs/CAVEATS_AND_SCOPE.md** — What the system can and cannot answer; “mentioned / discussed / quoted / invoice-like / ordered-like / confirmed sold”; language to use in UI (e.g. “most mentioned”, “most requested”, “most quoted”, “most commercially signaled”) and what never to claim without ERP reconciliation.

**Phase 7 deliverables:** Refactors, tests, READMEs, DATA_MODEL.md, CAVEATS_AND_SCOPE.md. Final “what this can and cannot answer” section (e.g. in README or CAVEATS).

---

## Implementation order and dependencies

```
Phase 1 (Audit)     → done
Phase 2 (Extraction) → schema/parsing changes; enables better body and threads for Phase 3–4
Phase 3 (Entities)   → depends on Phase 2 for body/threads; feeds Phase 4 marts
Phase 4 (Marts)      → depends on Phase 3; feeds Phase 5 dashboard
Phase 5 (Dashboard) → depends on Phase 4
Phase 6 (ML)        → after 4–5; optional enhancements
Phase 7 (Quality)   → ongoing; doc and test deliverables at end of each phase
```

**Next step:** Implement Phase 2 in small commits (e.g. 2.1 body, then 2.2 quote/signature, then 2.3 attachments, 2.4 dedupe diagnostics, 2.5 threads), with tests and a brief summary after each sub-step.
