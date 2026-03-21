# External Lead Intelligence for Chile — Implementation Plan

> **Superseded for day-to-day use.** The pipeline described here was implemented. For current commands, tables, and outputs see **[LEAD_PIPELINE.md](LEAD_PIPELINE.md)**. Keep this file as **historical design context** (decisions and original structure), not as status of the repo.

**Original status note:** Plan only (pre-implementation).  
**Scope (historical):** New module inside OrigenLab repo; no PST changes.

---

## 1. Repo-aware implementation plan (overview)

- **Same SQLite DB** as email archive and business mart (`resolved_sqlite_path()`). Add new tables only; no change to `emails`, `attachments`, `organization_master`, etc.
- **No changes to `db.py` init_schema** for the email pipeline. Lead tables are created by the leads build script on first run (same pattern as “run mart build” creating mart tables).
- **New package surface:** `src/origenlab_email_pipeline/leads_*.py` and `scripts/leads/`. Config stays as-is; optional env vars only for API keys or cache paths later.
- **Equipment keywords:** Reuse and extend the existing `_EQUIPMENT_PATTERNS` / `equipment_tags_from_text()` from `business_mart.py` via a small shared layer so leads can tag and score by the same tags the mart uses.
- **Matching:** Read-only queries against `organization_master` (domain, normalized name). No writes to mart tables from the leads pipeline.

**Data flow (v1):**

1. **Ingest** — Scripts fetch or load raw data from ChileCompra (Datos Abiertos / file), INN (CSV or minimal fetch), CORFO (CSV or minimal fetch) → insert into `external_leads_raw`.
2. **Normalize** — One script reads `external_leads_raw`, parses and normalizes into `lead_master` (one row per logical lead; dedupe by source + source_record_id or by org name + source).
3. **Score** — Same or next step: compute `priority_score`, set `equipment_match_tags`, `organization_type_guess`, `lead_type`.
4. **Match** — Optional step: join `lead_master` to `organization_master` on domain (and optionally normalized name), write results to `lead_matches_existing_orgs`.
5. **Export** — Script exports `lead_master` (and optional match columns) to CSV for review and outreach.

---

## 2. Proposed folder and file structure

```
# New / modified
scripts/leads/
  README.md                    # Short “how to run” and source notes
  run_leads_pipeline.sh        # Orchestrate: fetch → normalize → score → match → export (optional steps)
  fetch_chilecompra.py         # ChileCompra / Mercado Público: file or API
  fetch_inn_labs.py           # INN accredited labs: CSV or minimal crawl
  fetch_corfo_centers.py       # CORFO I+D centers: CSV or minimal crawl
  normalize_leads.py           # raw → lead_master
  score_leads.py               # compute priority_score, equipment tags, lead_type (can be merged into normalize_leads.py in v1)
  match_leads_to_mart.py       # lead_master ↔ organization_master → lead_matches_existing_orgs
  export_leads_csv.py          # lead_master (+ match info) → CSV

src/origenlab_email_pipeline/
  leads_schema.py              # LEAD_SCHEMA_SQL, ensure_leads_tables(conn)
  leads_ingest.py               # Helpers: insert_raw, dedupe key, source_name constants
  leads_normalize.py            # Raw → normalized fields (org_name, domain, region, contact, etc.)
  leads_score.py               # priority_score, equipment_match_tags, lead_type
  leads_match.py               # Match to organization_master, write lead_matches_existing_orgs
  leads_equipment.py           # Equipment keyword list + tag function (reuse business_mart patterns, extend for procurement Spanish)

docs/
  LEAD_PIPELINE.md              # User-facing: what it is, how to run, sources, CSV export, matching
  CHILE_LEAD_SOURCES.md        # (existing) Keep; reference from LEAD_PIPELINE.md
```

**Naming:** `leads_*` in `src` keeps the module clearly separate from `business_mart`, `parse_mbox`, `db`, etc. Scripts under `scripts/leads/` mirror `scripts/ingest/`, `scripts/mart/`, `scripts/reports/`.

**What we do not add in v1:** No new Streamlit tab, no new app file. Export = CSV + optional `sqlite3` / script-based inspection.

---

## 3. Proposed SQLite schema

**Database:** Same as today (`ORIGENLAB_SQLITE_PATH` / `data_root/sqlite/emails.sqlite`). New tables are additive.

### 3.1 `external_leads_raw`

One row per raw record from an external source. Purpose: idempotent re-fetch, debugging, and reprocessing without re-scraping.

| Column            | Type    | Description |
|-------------------|---------|-------------|
| id                | INTEGER | PK AUTOINCREMENT |
| source_name       | TEXT    | e.g. `chilecompra`, `inn_labs`, `corfo_centers` |
| source_record_id  | TEXT    | External ID (tender code, lab ID, center ID) |
| fetched_at        | TEXT    | ISO datetime UTC |
| raw_json          | TEXT    | Full payload as JSON (or NULL if we only store extracted fields) |
| source_url        | TEXT    | Canonical URL to the record (optional) |
| UNIQUE(source_name, source_record_id) | | Prevent duplicate raw rows |

Indexes: `(source_name, source_record_id)`, `(source_name, fetched_at)`.

### 3.2 `lead_master`

Normalized lead table for prospecting. One row per logical lead; deduplication by (source_name, org/entity key) or by (source_name, source_record_id) depending on source.

| Column                  | Type    | Description |
|-------------------------|---------|-------------|
| id                      | INTEGER | PK AUTOINCREMENT |
| source_name             | TEXT    | Same as raw |
| source_type             | TEXT    | `procurement` \| `accredited_lab` \| `research_center` |
| source_record_id        | TEXT    | Link back to raw |
| source_url              | TEXT    | |
| org_name                | TEXT    | Organization / buyer / lab name |
| contact_name             | TEXT    | When available |
| email                   | TEXT    | |
| phone                   | TEXT    | |
| website                 | TEXT    | |
| domain                  | TEXT    | Normalized for matching (from email or URL) |
| region                  | TEXT    | Chilean region |
| city                    | TEXT    | |
| lead_type               | TEXT    | e.g. `tender_buyer`, `accredited_lab`, `corfo_center` |
| organization_type_guess | TEXT    | Same semantics as mart: `education`, `government`, `business`, `consumer_email` |
| equipment_match_tags     | TEXT    | Comma-separated tags from leads_equipment |
| evidence_summary         | TEXT    | Short free text (e.g. “Licitación: balanza analítica”) |
| first_seen_at            | TEXT    | ISO datetime |
| last_seen_at             | TEXT    | ISO datetime (updated on re-fetch) |
| priority_score           | REAL    | 0–10+ explainable score |
| status                  | TEXT    | `nuevo` \| `revisado` \| `priorizado` \| `contactado` \| `descartado` |
| notes                   | TEXT    | Manual / script notes |

Indexes: `(source_name)`, `(domain)`, `(status)`, `(priority_score DESC)`, `(last_seen_at)`.

### 3.3 `lead_matches_existing_orgs`

Optional matching layer: which lead matches which existing organization in the email archive.

| Column                 | Type    | Description |
|------------------------|---------|-------------|
| id                     | INTEGER | PK AUTOINCREMENT |
| lead_id                | INTEGER | FK → lead_master.id |
| matched_domain         | TEXT    | organization_master.domain |
| matched_org_name       | TEXT    | organization_master.organization_name_guess |
| match_type             | TEXT    | `domain` \| `domain_and_name` \| `name_fuzzy` |
| confidence_score       | REAL    | 0–1 |
| already_in_archive_flag| INTEGER | 1 if match found, 0 otherwise |

Index: `(lead_id)`, `(matched_domain)`.

**Refinements vs your draft:**

- `external_leads_raw` keeps `raw_json` so we can re-run normalization without re-fetching.
- `lead_master.source_type` and `lead_type` distinguish “kind of source” vs “kind of entity” (e.g. procurement vs lab vs center).
- `lead_master.domain` is the main join key to `organization_master.domain`; we derive it from email or website URL when possible.
- Status values exactly as you specified: `nuevo`, `revisado`, `priorizado`, `contactado`, `descartado`.

---

## 4. Proposed scripts to create

| Script | Purpose | Input | Output |
|--------|---------|--------|--------|
| `fetch_chilecompra.py` | Load ChileCompra / Mercado Público data | Datos Abiertos file path or API (if configured) | `external_leads_raw` rows |
| `fetch_inn_labs.py`     | Load INN accredited labs | CSV path or (v1) built-in sample / minimal HTTP | `external_leads_raw` rows |
| `fetch_corfo_centers.py`| Load CORFO I+D centers  | CSV path or (v1) built-in sample / minimal HTTP | `external_leads_raw` rows |
| `normalize_leads.py`    | Raw → lead_master       | `external_leads_raw` | `lead_master` (insert/update by source + key) |
| `score_leads.py`        | Set priority_score, equipment_match_tags, lead_type, organization_type_guess | `lead_master` | Same table updated |
| `match_leads_to_mart.py`| Match to organization_master | `lead_master`, `organization_master` | `lead_matches_existing_orgs` |
| `export_leads_csv.py`   | Export to CSV           | `lead_master` (+ optional join to matches) | One CSV file |
| `run_leads_pipeline.sh` | Run full pipeline       | — | Runs fetch → normalize → score → match → export (with flags to skip fetch or match) |

In v1, **normalize** and **score** can be one script (`normalize_leads.py`) that both normalizes and scores in one pass to reduce moving parts.

**CLI pattern (aligned with repo):** `uv run python scripts/leads/fetch_chilecompra.py [--file PATH]`, `uv run python scripts/leads/normalize_leads.py`, etc. All use `load_settings().resolved_sqlite_path()` and the same `connect()` from `db.py`.

---

## 5. Source-by-source ingestion strategy

### A. ChileCompra / Mercado Público

- **Purpose:** Detect active/public procurement opportunities; identify buyer entities; capture tender title, buyer name, URLs, dates.
- **v1 approach:** Prefer **Datos Abiertos** (datos-abiertos.chilecompra.cl) bulk files (tenders, purchase orders, or buyer “fichas”) if available as CSV/JSON. Script reads a **local file** (e.g. downloaded manually or by a separate job) and parses rows; filter by equipment keyword pack on title/description; insert into `external_leads_raw` with `source_name='chilecompra'`, `source_record_id` = tender/PO ID.
- **Alternative:** Mercado Público API requires a ticket (Clave Única). v1 does **not** depend on it; we document “for production, use API + ticket and point fetch script at API”. Optional: `--api-ticket` and small client for “licitaciones activas” in a later iteration.
- **Fields to extract:** Buyer org name, tender/PO ID, title, description snippet, publication/close date, source URL. Store in `raw_json`; normalize into `lead_master` with `lead_type='tender_buyer'`, `org_name` = buyer, `evidence_summary` = title or snippet.

### B. INN accredited labs

- **Purpose:** Stable list of accredited laboratories; org name, accreditation area, region, website/contact if public.
- **v1 approach:** **CSV ingestion.** Document the expected CSV format (columns: lab name, area/scheme, region, website, contact if any). Script `fetch_inn_labs.py` reads CSV from `--file` and inserts into `external_leads_raw` with `source_name='inn_labs'`. If INN provides an export or we produce a sample CSV from directorio.inn.cl (manual export), the same script works. Optional later: minimal HTTP fetcher with rate limiting and clear User-Agent, only if compliant with INN’s terms.
- **Fields:** Lab name → `org_name`, accreditation area → `evidence_summary` or a dedicated column, region, website, contact.

### C. CORFO research / I+D centers

- **Purpose:** Research and innovation centers that may need equipment; center name, organization, region, website, contact.
- **v1 approach:** Same as INN: **CSV ingestion** from `--file`. Document expected columns (center name, organization, region, website, contact name/email/phone). Script `fetch_corfo_centers.py` reads CSV and inserts into `external_leads_raw` with `source_name='corfo_centers'`. Optional later: controlled fetch from sgp.corfo.cl if allowed.
- **Fields:** Center name, hosting org → `org_name`, region, website, contact → normalize into `contact_name`, `email`, `phone`.

**Idempotency:** For each source, use `(source_name, source_record_id)` as unique key; `INSERT OR REPLACE` or `INSERT OR IGNORE` + update `fetched_at` so re-runs do not duplicate raw rows.

**Compliance:** Only public data; prefer official downloads and documented APIs; no aggressive scraping in v1.

---

## 6. Lead scoring approach (v1)

Simple, explainable **priority_score** (0–10+, stored in `lead_master`):

| Factor | Points | Notes |
|--------|--------|--------|
| Source strength | 0–2 | procurement = 2, accredited_lab = 1.5, research_center = 1 |
| Procurement intent | 0–2 | Active tender with equipment keywords = 2; else 0 for non-procurement |
| Research/lab relevance | 0–2 | accredited_lab or corfo_center = 1.5–2; else 0 |
| Equipment match | 0–2 | Number of equipment tags (cap at 2): 1 tag = 0.5, 2+ = 2 |
| Contact info present | 0–1 | email or phone or both = 1 |
| Already in archive (match) | -1 or 0 | If matched to organization_master, optionally reduce score so “net new” leads rank higher (v1 can skip this and only report match in export) |

Sum = priority_score. Keep logic in `leads_score.py` with small, testable functions (e.g. `score_source_type()`, `score_equipment_tags()`, `score_contact_info()`).

**lead_type** and **organization_type_guess:** Set in the same pass. `organization_type_guess` reuses the same heuristics as the mart (e.g. `guess_org_type_from_domain` in `business_mart.py`) when we have a domain; otherwise infer from org name/source (e.g. “universidad” → education, “gob.cl” → government).

---

## 7. Equipment keyword pack and tagging

- **Where:** New module `src/origenlab_email_pipeline/leads_equipment.py`.
- **Content:** Define the same tag set as the mart (balanza, centrifuga, cromatografia_hplc, microscopio, phmetro, autoclave, humedad_granos, etc.). Either:
  - **Option A:** Import `equipment_tags_from_text` from `business_mart` and add procurement-specific Spanish phrases in a second pass (e.g. “balanza analítica”, “centrífuga refrigerada”) that map to the same tags, or
  - **Option B:** Define in `leads_equipment.py` a single list of (tag, pattern) used only for leads, and keep mart’s list as-is (duplication but full separation).  
- **Recommendation:** Option A: add `leads_equipment.py` with a function `equipment_tags_for_leads(text: str) -> list[str]` that calls `equipment_tags_from_text(text)` and optionally runs extra Spanish procurement patterns that map into the same tag names. That way one canonical tag set lives in `business_mart`; leads extend only the *phrases*, not the schema of tags.
- **Tagging:** In `leads_normalize` / `leads_score`, concatenate title + description + evidence_summary and call `equipment_tags_for_leads(...)`; store result as comma-separated in `lead_master.equipment_match_tags`.

---

## 8. Matching strategy to existing business mart

- **Goal:** Know if a lead is already in the email archive (same org), net-new, or possibly related.
- **v1 matching (minimal):**
  - **Domain:** Normalize lead’s `domain` (from email or parsed from website). If `domain` is present, `SELECT 1 FROM organization_master WHERE domain = ?`. If found → match_type = `domain`, confidence = 1.0, set `already_in_archive_flag = 1`.
  - **Name fallback:** If no domain, optionally normalize `org_name` (lowercase, strip accents, remove common suffixes like “S.A.”, “SpA”) and compare to `organization_master.organization_name_guess` with a simple similarity (e.g. substring or normalized equality). If match → match_type = `name_fuzzy`, confidence = 0.6–0.8. Do not over-engineer in v1.
- **Write:** For each lead with at least one match, insert into `lead_matches_existing_orgs` (lead_id, matched_domain, matched_org_name, match_type, confidence_score, already_in_archive_flag=1). One row per (lead_id, matched_domain).
- **No writes to mart:** Only read `organization_master`. Matching is one-way: leads → mart.

---

## 9. Suggested docs to add

| Doc | Content |
|-----|--------|
| **docs/LEAD_PIPELINE.md** | User-facing: what the lead pipeline is, the three sources, how to run it (commands), CSV export, how matching works, status values, where to put CSV files for fetch, optional env vars. Link to CHILE_LEAD_SOURCES.md and LEAD_PIPELINE_PLAN.md. |
| **docs/CHILE_LEAD_SOURCES.md** | Already exists; keep. Reference from LEAD_PIPELINE.md for keyword packs and source URLs. |
| **scripts/leads/README.md** | Short: list of scripts, order of execution, `run_leads_pipeline.sh` usage, and “expected CSV formats” for INN and CORFO (and ChileCompra file if file-based). |

No separate “API design” doc for v1; CLI and schema are the contract.

---

## 10. Recommended v1 vs v2 boundary

**Build in v1:**

- Schema: `external_leads_raw`, `lead_master`, `lead_matches_existing_orgs`.
- Scripts: fetch (file-based for all three sources; ChileCompra = file, INN = CSV, CORFO = CSV), normalize (+ score in same pass), match, export CSV.
- Equipment: reuse mart tags via `leads_equipment.equipment_tags_for_leads()`.
- Scoring: explainable 0–10+ in `leads_score.py`.
- Matching: domain exact match + optional name fallback; read-only from `organization_master`.
- Docs: LEAD_PIPELINE.md, scripts/leads/README.md, this plan.
- One orchestration script: `run_leads_pipeline.sh` (run all steps; flags to skip fetch or match).

**Defer to v2:**

- Streamlit tab “Prospección” / “Leads externos” (v1 = CSV + SQLite inspection only).
- Mercado Público API (ticket + real-time); v1 uses file only.
- Automated HTTP crawl for INN/CORFO (v1 = CSV only).
- Embeddings / semantic matching for “similar to existing customer”.
- Enrichment (e.g. domain lookup, extra contact data).
- Status updates from UI (v1 = manual CSV edit or DB update).

---

## 11. Exact commands to run (v1)

Assumes repo root and `uv` + env already set up.

```bash
# 1) Ensure DB exists (e.g. from existing pipeline)
uv run python -c "from origenlab_email_pipeline.config import load_settings; from origenlab_email_pipeline.db import connect, init_schema; conn = connect(load_settings().resolved_sqlite_path()); init_schema(conn); conn.close()"

# 2) Create lead tables (first time only; idempotent)
uv run python scripts/leads/normalize_leads.py --ensure-schema-only

# 3) Ingest raw data (files you prepared)
uv run python scripts/leads/fetch_chilecompra.py --file ~/data/origenlab-email/leads/chilecompra_tenders.csv
uv run python scripts/leads/fetch_inn_labs.py --file ~/data/origenlab-email/leads/inn_labs.csv
uv run python scripts/leads/fetch_corfo_centers.py --file ~/data/origenlab-email/leads/corfo_centers.csv

# 4) Normalize + score
uv run python scripts/leads/normalize_leads.py

# 5) Match to existing orgs (optional; requires mart built)
uv run python scripts/leads/match_leads_to_mart.py

# 6) Export CSV
uv run python scripts/leads/export_leads_csv.py --out ~/data/origenlab-email/leads/leads_export.csv

# Or run full pipeline (fetch steps require files; normalize/score/match/export use DB)
bash scripts/leads/run_leads_pipeline.sh
# With options, e.g.:
#   bash scripts/leads/run_leads_pipeline.sh --skip-fetch --export reports/out/leads.csv
```

`--ensure-schema-only` in (2) would only create lead tables and exit; the same script without that flag runs normalize+score.

---

## 12. Assumptions

- Same SQLite file as the rest of the project; no separate “leads DB”.
- Mart may or may not exist; matching script no-ops or warns if `organization_master` is empty.
- ChileCompra v1 = file-based (Datos Abiertos download or manual export); INN and CORFO v1 = CSV with documented column names.
- Users are okay preparing CSV/files manually for v1 (or we ship minimal sample CSVs in repo for testing).
- Status and notes in `lead_master` are updated manually (or via one-off SQL) in v1.
- Equipment tag set stays aligned with mart (same tag names) so future UI or reports can share dimensions.

---

## 13. Risks and fragilities

- **Source availability:** ChileCompra file format or URL may change; INN/CORFO may change export or site structure. Mitigation: document expected formats; keep raw in `external_leads_raw` for reprocessing.
- **Domain parsing:** Many leads will have no email; domain from website URL is best-effort (e.g. strip www, take hostname). Some leads will have no domain → matching only by name, weaker.
- **Duplicate leads:** Same org from two sources (e.g. INN and ChileCompra) can produce two `lead_master` rows. v1 does not merge; we can add dedupe by normalized org_name + domain in v2.
- **Scoring subjectivity:** Weights (0–2, 0–1) are heuristic; we keep them in code and doc so they can be tuned.
- **Legal/compliance:** We assume use of official/open data and documented APIs; any future crawl must respect robots.txt and terms of use.

---

## 14. Where manual review is still necessary

- **Deciding which leads to contact:** Export is input to human review; status updates (revisado, priorizado, contactado, descartado) are manual in v1.
- **Preparing input files:** Downloading ChileCompra data, exporting INN/CORFO to CSV (or running a future crawler) may require manual steps.
- **Enrichment:** Adding contact emails/phones for leads that only have org name is out of scope for v1; can be spreadsheet or external tooling.
- **Merging duplicates:** If the same organization appears from multiple sources, merging into one lead is manual or a later script.

---

## 15. Summary

| Item | Proposal |
|------|----------|
| **Structure** | `scripts/leads/*.py` + `src/.../leads_*.py` + `docs/LEAD_PIPELINE.md`, `docs/CHILE_LEAD_SOURCES.md` (existing) |
| **Schema** | `external_leads_raw`, `lead_master`, `lead_matches_existing_orgs` in same SQLite |
| **Sources v1** | ChileCompra (file), INN (CSV), CORFO (CSV) |
| **Scoring** | Explainable 0–10+ (source + intent + equipment + contact) |
| **Matching** | Domain exact + optional name; read-only from organization_master |
| **Equipment** | Reuse mart tags; `leads_equipment.py` extends phrases for procurement Spanish |
| **Export** | CSV only in v1; no Streamlit tab yet |
| **Commands** | fetch_* (--file), normalize_leads, match_leads_to_mart, export_leads_csv; optional run_leads_pipeline.sh |

This plan is implementation-ready pending your approval. No code has been written yet; naming and layout can be adjusted if you prefer different conventions.
