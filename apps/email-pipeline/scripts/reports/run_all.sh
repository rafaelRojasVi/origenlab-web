#!/usr/bin/env bash
# Run report + stratified clusters + ML explore in one go (same batch folder).
#
#   bash scripts/reports/run_all.sh
#   SKIP_EMBEDDINGS=1 bash scripts/reports/run_all.sh          # faster, no GPU model load
#   WITH_EMBEDDINGS=1 bash scripts/reports/run_all.sh          # full report incl. embeddings (~3500)
#   NAME=myclient bash scripts/reports/run_all.sh
#
# Needs: emails.sqlite, uv sync --group ml

set -euo pipefail
# Run from repo root (parent of scripts/)
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
NAME="${NAME:-batch_$(date +%Y%m%d_%H%M%S)}"
BATCH="${ORIGENLAB_REPORTS_DIR:-$HOME/data/origenlab-email/reports}/run_${NAME}"
REPORT_DIR="$BATCH/client_report"
mkdir -p "$BATCH"

echo "========== OrigenLab — run all =========="
echo "Output: $BATCH"
echo ""

DB="${ORIGENLAB_SQLITE_PATH:-$HOME/data/origenlab-email/sqlite/emails.sqlite}"
if [[ ! -f "$DB" ]]; then
  echo "SQLite not found: $DB"
  echo "Build: uv run python scripts/ingest/02_mbox_to_sqlite.py"
  exit 1
fi

EMBED=(--embeddings-sample 0)
if [[ "${WITH_EMBEDDINGS:-}" == "1" ]]; then
  EMBED=( )   # --full will add embeddings
fi

echo ">>> 1/4 Client report (SQL + dominios paralelos) …"
if [[ "${WITH_EMBEDDINGS:-}" == "1" ]]; then
  uv run python scripts/reports/generate_client_report.py --full --out "$REPORT_DIR" --name "_"
else
  uv run python scripts/reports/generate_client_report.py --full --embeddings-sample 0 --out "$REPORT_DIR" --name "_"
fi
# generate_client_report appends timestamp_name to folder — normalize to REPORT_DIR
# Actually --out "$REPORT_DIR" means out_dir is REPORT_DIR directly, run_id still has timestamp
echo "    → $REPORT_DIR/index.html"

echo ">>> 2/4 Clusters sample no_bounce …"
uv run python scripts/ml/explore_email_clusters.py --limit 2000 --sample-mode no_bounce \
  --n-clusters 14 --report-dir "$REPORT_DIR" || true
if [[ -f "$REPORT_DIR/explore_clusters.json" ]]; then
  mv "$REPORT_DIR/explore_clusters.json" "$REPORT_DIR/clusters_no_bounce.json"
  echo "    → clusters_no_bounce.json"
fi

echo ">>> 3/4 Clusters sample cotiz …"
uv run python scripts/ml/explore_email_clusters.py --limit 1500 --sample-mode cotiz \
  --n-clusters 12 --report-dir "$REPORT_DIR" || true
if [[ -f "$REPORT_DIR/explore_clusters.json" ]]; then
  mv "$REPORT_DIR/explore_clusters.json" "$REPORT_DIR/clusters_cotiz.json"
  echo "    → clusters_cotiz.json"
fi

echo ">>> 4/4 ML explore (K-Means + model regex) …"
uv run python scripts/ml/email_ml_explore.py --limit 4500 --kmeans 16 --out "$BATCH/ml_explore.json"
echo "    → ml_explore.json"

echo ">>> ML report (HTML con gráficos de KMeans + equipos) …"
uv run python scripts/reports/build_ml_report.py --batch "$BATCH" || true
echo "    → ml_report.html"

echo ">>> Overview page (one place for all results) …"
uv run python scripts/mart/build_batch_overview.py --batch "$BATCH" || true
echo "    → overview.html"

echo ""
echo "========== Done =========="
echo "One-page overview (what ran + numbers + links):  $BATCH/overview.html"
echo "Full report (SQL + embeddings):   $REPORT_DIR/index.html"
echo "ML report (KMeans + equipos, gráficos):  $BATCH/ml_report.html"
echo "ML raw JSON:   $BATCH/ml_explore.json"
echo "Open browser:"
echo "  uv run python scripts/mart/open_client_report.py --open"
echo "(Latest report dir may differ if you use default reports path — use folder above)"
