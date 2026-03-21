# Run everything at once

One shell script runs, in order:

1. **Full client report** — SQL merged + año×cotiz + dominios en paralelo + `index.html` / `summary.json` / `ALCANCE_INFORME.md`
2. **Clusters (no_bounce)** — embeddings + agglomerative → `clusters_no_bounce.json`
3. **Clusters (cotiz)** → `clusters_cotiz.json`
4. **ML explore** — K-Means + regex model mentions → `ml_explore.json`
5. **Overview page** — `build_batch_overview.py` writes `overview.html` in the batch folder: one page with “what ran”, key numbers, and links to all outputs (see [OUTPUTS_OVERVIEW.md](OUTPUTS_OVERVIEW.md)).

## Command

```bash
cd apps/email-pipeline   # from OrigenLab monorepo root
uv sync --group ml
chmod +x scripts/reports/run_all.sh
bash scripts/reports/run_all.sh
```

Default output folder:

`~/data/origenlab-email/reports/run_batch_YYYYMMDD_HHMMSS/`

- **`overview.html`** — open this first: checklist of what ran, key numbers, links to all files.
- **`client_report/index.html`** — full report (charts, tables).
- **`client_report/summary.json`**, **`clusters*.json`**, **`ml_explore.json`** — data files.

## Options (env)

| Variable | Effect |
|----------|--------|
| `NAME=myclient` | Folder `run_myclient` |
| `WITH_EMBEDDINGS=1` | Report also runs GPU embeddings (~3500) inside step 1 (longer) |
| `ORIGENLAB_REPORTS_DIR` | Where to create `run_*` |
| `ORIGENLAB_SQLITE_PATH` | DB path |

Examples:

```bash
NAME=marzo2025 bash scripts/reports/run_all.sh
WITH_EMBEDDINGS=1 NAME=full_gpu bash scripts/reports/run_all.sh
```

## Time

Rough order: **~5–15 min** on ~130k rows (SQL + 16 workers dominios + 2× cluster samples + ml explore), more with `WITH_EMBEDDINGS=1`.

## Open result

```bash
# Or open the printed path …/client_report/index.html
xdg-open ~/data/origenlab-email/reports/run_batch_*/client_report/index.html
```

Not included in `run_all.sh`: PST→mbox→SQLite (run those separately when raw mail changes).
