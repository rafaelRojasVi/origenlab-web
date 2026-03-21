# What to run after importing PST → SQLite

After `02_mbox_to_sqlite.py` finishes, run in this order:

---

## Run everything at once (recommended)

Generates all reports into one timestamped folder: unique emails CSV, client HTML + summary, business filter artifacts (category counts, sender domains, sample).

```bash
cd apps/email-pipeline   # from OrigenLab monorepo root
uv run python scripts/reports/run_all_reports.py
```

Options:

- `--out DIR` — use a specific output directory instead of `reports/out/full_YYYYMMDD_HHMMSS`
- `--fast` — skip full domain scan in client report (faster, fewer top-domains)
- `--embeddings` — run ML embeddings + clusters (needs GPU/CUDA and ML deps)
- `--dedupe` — run dedupe by Message-ID before generating reports

Output folder will contain: `unique_emails.csv`, `index.html`, `summary.json`, `ALCANCE_INFORME.md`, `business_filter_summary.json`, `business_only_sample.json`, `category_counts.csv`, `sender_domain_by_view.csv`.

---

## 1. Deduplicate (recommended first, or use --dedupe in run_all_reports)

Same message can appear in multiple PSTs. Dedupe by `Message-ID` so counts and reports are accurate.

```bash
cd apps/email-pipeline   # from OrigenLab monorepo root
uv run python scripts/tools/dedupe_emails_by_message_id.py
```

Example output: `Before: 590,606 rows | After: 5XX,XXX rows | Removed: XX,XXX duplicates`

---

## 2. Reports

### A. Unique emails CSV (contacts list)

```bash
uv run python scripts/tools/export_unique_emails_csv.py --out reports/out/unique_emails.csv
```

### B. Business filter report (categories, top domains, sample)

Full run (all emails, can take a while):

```bash
uv run python scripts/reports/generate_business_filter_report.py --out reports/out/bf_full
```

Faster test on a sample:

```bash
uv run python scripts/reports/generate_business_filter_report.py --out reports/out/bf_sample --limit 50000
```

### C. Client report (HTML + summary + charts)

Quick run (no domain streaming, no embeddings):

```bash
uv run python scripts/reports/generate_client_report.py --fast --out reports/out/client_report
```

Full run (with top domains; add `--embeddings-sample 1500` if you want ML clusters):

```bash
uv run python scripts/reports/generate_client_report.py --out reports/out/client_report
```

---

## One-liner (dedupe + unique emails + business filter)

```bash
cd apps/email-pipeline && \   # from OrigenLab monorepo root
uv run python scripts/tools/dedupe_emails_by_message_id.py && \
uv run python scripts/tools/export_unique_emails_csv.py --out reports/out/unique_emails.csv && \
uv run python scripts/reports/generate_business_filter_report.py --out reports/out/bf_full
```

Then open `reports/out/` for the CSVs and JSON. Run the client report separately if you want the HTML dashboard.
