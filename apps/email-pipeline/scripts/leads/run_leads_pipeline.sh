#!/usr/bin/env bash
# Run the v1 lead pipeline: ensure schema → fetch (from files) → normalize → score → match → export.
#
# Usage:
#   bash scripts/leads/run_leads_pipeline.sh
#   bash scripts/leads/run_leads_pipeline.sh --skip-fetch
#   bash scripts/leads/run_leads_pipeline.sh --skip-fetch --export-only
#
# Set LEADS_CHILECOMPRA_FILE, LEADS_INN_FILE, LEADS_CORFO_FILE to point to your input files.
# Set LEADS_EXPORT_PATH for CSV output (default: reports/out/leads_export.csv under repo).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

LEADS_EXPORT_PATH="${LEADS_EXPORT_PATH:-$ROOT/reports/out/leads_export.csv}"
LEADS_CHILECOMPRA_FILE="${LEADS_CHILECOMPRA_FILE:-}"
LEADS_INN_FILE="${LEADS_INN_FILE:-}"
LEADS_CORFO_FILE="${LEADS_CORFO_FILE:-}"

echo "========== OrigenLab Lead Pipeline (v1) =========="
echo ""

# 1) Ensure schema
echo ">>> 1/6 Ensure lead tables..."
uv run python scripts/leads/normalize_leads.py --ensure-schema-only
echo ""

# 2–4) Ingest from files (skip if --skip-fetch or file not set)
if [[ "${1:-}" != "--skip-fetch" && "${1:-}" != "--export-only" ]]; then
  if [[ -n "$LEADS_CHILECOMPRA_FILE" && -f "$LEADS_CHILECOMPRA_FILE" ]]; then
    echo ">>> 2/6 Ingest ChileCompra from $LEADS_CHILECOMPRA_FILE..."
    uv run python scripts/leads/fetch_chilecompra.py --file "$LEADS_CHILECOMPRA_FILE"
  elif [[ -n "$LEADS_CHILECOMPRA_FILE" ]]; then
    echo ">>> 2/6 Skip ChileCompra (file not found: $LEADS_CHILECOMPRA_FILE)"
  else
    echo ">>> 2/6 Skip ChileCompra (set LEADS_CHILECOMPRA_FILE; e.g. scripts/leads/samples/chilecompra_sample.csv)"
  fi
  if [[ -n "$LEADS_INN_FILE" && -f "$LEADS_INN_FILE" ]]; then
    echo ">>> 3/6 Ingest INN labs from $LEADS_INN_FILE..."
    uv run python scripts/leads/fetch_inn_labs.py --file "$LEADS_INN_FILE"
  elif [[ -n "$LEADS_INN_FILE" ]]; then
    echo ">>> 3/6 Skip INN (file not found: $LEADS_INN_FILE)"
  else
    echo ">>> 3/6 Skip INN (set LEADS_INN_FILE; e.g. scripts/leads/samples/inn_labs_sample.csv)"
  fi
  if [[ -n "$LEADS_CORFO_FILE" && -f "$LEADS_CORFO_FILE" ]]; then
    echo ">>> 4/6 Ingest CORFO centers from $LEADS_CORFO_FILE..."
    uv run python scripts/leads/fetch_corfo_centers.py --file "$LEADS_CORFO_FILE"
  elif [[ -n "$LEADS_CORFO_FILE" ]]; then
    echo ">>> 4/6 Skip CORFO (file not found: $LEADS_CORFO_FILE)"
  else
    echo ">>> 4/6 Skip CORFO (set LEADS_CORFO_FILE; e.g. scripts/leads/samples/corfo_centers_sample.csv)"
  fi
else
  echo ">>> 2–4/6 Skip fetch (--skip-fetch or --export-only)"
fi
echo ""

echo ">>> 5/6 Normalize and score leads..."
uv run python scripts/leads/normalize_leads.py
uv run python scripts/leads/leads_score.py
echo ""

echo ">>> 6/6 Match to mart and export..."
uv run python scripts/leads/match_leads_to_mart.py
mkdir -p "$(dirname "$LEADS_EXPORT_PATH")"
uv run python scripts/leads/export_leads_csv.py --out "$LEADS_EXPORT_PATH"
SHORTLIST_PATH="${LEADS_SHORTLIST_PATH:-$ROOT/reports/out/leads_shortlist.csv}"
uv run python scripts/leads/export_leads_shortlist.py --out "$SHORTLIST_PATH" --limit "${LEADS_SHORTLIST_LIMIT:-200}"
echo ""
echo "========== Done =========="
echo "Export: $LEADS_EXPORT_PATH"
echo "Shortlist: $SHORTLIST_PATH"
