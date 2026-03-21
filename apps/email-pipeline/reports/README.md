# Client reports — not stored in this folder by default

HTML/JSON reports are written **outside the repo** so big outputs and client data stay next to your SQLite:

**Default location:** `~/data/origenlab-email/reports/<timestamp>_<name>/`

- `index.html` — open in a browser (double‑click or below)
- `summary.json`
- `clusters.json` (if you used embeddings)

## See the report “here” in the editor

1. **Open that folder in Cursor:** *File → Add Folder to Workspace…* →  
   `~/data/origenlab-email/reports`
2. Or run from the repo:
   ```bash
   uv run python scripts/mart/open_client_report.py --open
   ```
   **WSL:** `--open` uses Windows (`wslpath` + `cmd start`) so the report opens in Chrome/Edge on Windows. If Linux has no HTML app you’ll see `gio: Failed to find default application` — ignore; use `--open` again after updating the script, or open the printed **Windows path** in Explorer.

## Put reports inside the repo instead

```bash
mkdir -p reports/out
uv run python scripts/reports/generate_client_report.py --fast --out reports/out/mi_cliente
# opens: reports/out/mi_cliente/index.html
```

The root `.gitignore` already ignores generated files under `reports/out/` (except `README.md` and `.gitkeep` there).

## Env

`ORIGENLAB_REPORTS_DIR` — change the default reports root (see `.env.example`).
