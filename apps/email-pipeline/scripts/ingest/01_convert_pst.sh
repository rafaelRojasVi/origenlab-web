#!/usr/bin/env bash
# PST → mbox via readpst. Paths from env (same defaults as Python config).
set -euo pipefail

ROOT="${ORIGENLAB_DATA_ROOT:-$HOME/data/origenlab-email}"
INPUT_DIR="${ORIGENLAB_RAW_PST_DIR:-$ROOT/raw_pst}"
OUTPUT_DIR="${ORIGENLAB_MBOX_DIR:-$ROOT/mbox}"

if ! command -v readpst >/dev/null 2>&1; then
  echo "readpst not found. Install: sudo apt install -y pst-utils" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

found=0
while IFS= read -r -d '' pst; do
  found=1
  base="$(basename "$pst")"
  name="${base%.*}"
  out="$OUTPUT_DIR/$name"
  mkdir -p "$out"
  echo "Converting: $pst -> $out"
  readpst -o "$out" -r -D -j 4 "$pst" 2>/dev/null || readpst -o "$out" -r "$pst"
done < <(find "$INPUT_DIR" -type f \( -iname '*.pst' -o -iname '*.PST' \) -print0 2>/dev/null)

if [[ "$found" -eq 0 ]]; then
  echo "No .pst files under: $INPUT_DIR" >&2
  echo "Set ORIGENLAB_RAW_PST_DIR or ORIGENLAB_DATA_ROOT, or place PSTs there." >&2
  exit 1
fi

echo "Done. Mbox trees under: $OUTPUT_DIR"
