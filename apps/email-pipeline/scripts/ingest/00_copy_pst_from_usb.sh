#!/usr/bin/env bash
# Copy PSTs from Windows drives (F: and E:) into raw_pst, clearing old ones first.
# Run from WSL; F: = /mnt/f, E: = /mnt/e.
#
#   bash scripts/ingest/00_copy_pst_from_usb.sh

set -euo pipefail
ROOT="${ORIGENLAB_DATA_ROOT:-$HOME/data/origenlab-email}"
RAW="${ORIGENLAB_RAW_PST_DIR:-$ROOT/raw_pst}"
mkdir -p "$RAW"

# Remove existing PSTs so we replace with the new set
echo "Removing existing PSTs in $RAW …"
rm -f "$RAW"/*.pst "$RAW"/*.PST 2>/dev/null || true

# F: drive (quote paths with spaces)
if [[ -d /mnt/f ]]; then
  echo "Copying from F: (Archivos de Outlook) …"
  rsync -ah --info=progress2 --partial \
    "/mnt/f/Archivos de Outlook/backup.pst" \
    "/mnt/f/Archivos de Outlook/contacto@labdelivery.cl.pst" \
    "$RAW/" || echo "F: rsync failed (check path)."
else
  echo "F: not mounted. ls /mnt/ to see drives; or copy PSTs into $RAW from Windows (\\\\wsl.localhost\\Ubuntu\\home\\$USER\\data\\origenlab-email\\raw_pst)."
fi

# E: drive
if [[ -d /mnt/e ]]; then
  echo "Copying from E: …"
  rsync -ah --info=progress2 --partial \
    /mnt/e/backup1.pst \
    /mnt/e/backup2.pst \
    /mnt/e/backup3.pst \
    /mnt/e/backup4.pst \
    "$RAW/" || echo "E: rsync failed (check path)."
else
  echo "E: not mounted. Mount USBs or copy into raw_pst from Windows."
fi

echo "Done. PSTs in $RAW:"
ls -la "$RAW"/*.pst 2>/dev/null || { ls -la "$RAW"; echo "No PSTs yet — copy from Windows or mount F:/E: and re-run."; }
