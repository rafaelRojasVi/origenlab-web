# Scripts

One-off and pipeline CLI scripts. Run from the repo root with `uv run python scripts/<subdir>/<name>.py` (or `bash scripts/<subdir>/<name>.sh`). These are **not** installed as console entrypoints.

## Main entrypoints

| Task | Command |
|------|--------|
| **PST → mbox** | `bash scripts/ingest/01_convert_pst.sh` |
| **mbox → SQLite** | `uv run python scripts/ingest/02_mbox_to_sqlite.py` |
| **SQLite → JSONL** | `uv run python scripts/ingest/03_sqlite_to_jsonl.py` |
| **Build business mart** | `uv run python scripts/mart/build_business_mart.py --rebuild` |
| **Run Streamlit UI** | `uv run streamlit run apps/business_mart_app.py` |
| **Streamlit on LAN** | `bash scripts/tools/run_streamlit_lan.sh` (binds `0.0.0.0`; WSL2 needs Windows portproxy — see root `README.md`) |
| **Generate client report** | `uv run python scripts/reports/generate_client_report.py --fast --name <name>` |
| **Full run (reports + overview)** | `bash scripts/reports/run_all.sh` |
| **Inspect DB** | `uv run python scripts/tools/inspect_sqlite.py` |
| **Lead account rollup** | `uv run python scripts/build_lead_account_rollup.py` → `scripts/match_lead_accounts_to_existing_orgs.py` — see `docs/LEAD_ACCOUNT_LAYER.md` |
| **Audit lead org names** | `uv run python scripts/audit_lead_org_quality.py` |
| **Validate lead accounts** | `uv run python scripts/validate_lead_account_rollup.py` |

## Structure

### `scripts/ingest/` — Pipeline (PST → mbox → SQLite → JSONL)

- `00_copy_pst_from_usb.sh` — Copy PST from USB into raw dir (optional).
- `01_convert_pst.sh` — PST → mbox (requires `readpst`).
- `02_mbox_to_sqlite.py` — mbox → SQLite (full refresh of `emails`).
- `03_sqlite_to_jsonl.py` — SQLite → JSONL export.

### `scripts/mart/` — Business mart & report UX

- `build_business_mart.py` — Build/rebuild mart tables (contacts, orgs, docs, signals).
- `build_batch_overview.py` — Batch overview for report runs.
- `open_client_report.py` — Open latest or specified report folder.

### `scripts/reports/` — Client reports and full run

- `generate_client_report.py` — HTML + JSON client report (by year, domains, equipment, etc.).
- `generate_business_filter_report.py` — Business filter report.
- `run_all_reports.py` — Run report suite.
- `run_all.sh` — Full run: reports + overview (see `docs/RUN_ALL.md`).
- `build_ml_report.py` — Build ML report artifacts from explore output.

### `scripts/validation/` — Validation & extraction

- `validate_phase2_1.py`, `validate_phase2_2.py`, `validate_phase2_4_extracts.py` — Phase validation.
- `validate_attachments.py` — Attachment validation.
- `backfill_phase2_2_text_fields.py` — Backfill text fields for phase 2.2.
- `extract_attachment_text.py` — Extract text from attachments into DB.

### `scripts/ml/` — ML & embeddings

- `test_real_embeddings.py` — Smoke test embeddings on GPU (sentence-transformers).
- `explore_email_clusters.py` — Cluster emails by embeddings (optional report output).
- `email_ml_explore.py` — ML exploration output (e.g. `reports/out/ml.json`).

### `scripts/tools/` — DB and env utilities

- `inspect_sqlite.py` — Schema, counts, sample rows (default or given DB path).
- `export_unique_emails_csv.py` — Export unique emails to CSV.
- `dedupe_emails_by_message_id.py` — Deduplicate by Message-ID.
- `check_system.py`, `check_torch_cuda.py`, `check_embeddings_stack.py` — Environment checks.

## Paths

Scripts use **environment variables** (see root `.env.example`). Defaults assume data lives under `~/data/origenlab-email/` (raw_pst, mbox, sqlite, jsonl, reports, logs, tmp). Put real PSTs and heavy outputs **outside** the repo.
