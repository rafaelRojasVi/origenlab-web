# Informes para cliente (HTML + JSON)

Cada ejecución genera una **carpeta con fecha** bajo `ORIGENLAB_REPORTS_DIR` (por defecto `~/data/origenlab-email/reports/`).

## Qué incluye

| Artefacto | Contenido |
|-----------|-----------|
| `index.html` | Dashboard con gráficos (año, clasificación, equipos) y tablas |
| `summary.json` | Mismos datos en JSON (para Excel / BI) |
| `clusters.json` | (opcional) clusters de una muestra con embeddings |

### Clasificaciones (heurística sobre asunto + cuerpo)

- **Cotización** — `cotiz`
- **Proveedor** — palabra proveedor
- **Factura / invoice**
- **Pedido / OC** — pedido, purchase order, orden de compra
- **Universidad** — universidad, uchile, puc, utfsm, udec, .edu., etc.
- **Rebote / NDR** — mailer-daemon, delivery status, etc. (para contextualizar volumen)

### Equipamiento (menciones)

Microscopio, centrífuga, espectrofotómetro, pHmetro, autoclave, balanza, HPLC/cromatografía, incubadora, titulador, liofilizador, horno/mufla, pipetas, medidor humedad granos.

### Dominios / “quién más escribe”

- **Dominios que más envían** — dominio del `From` (proveedores / newsletters que entran).
- **Dominios en Para/Cc** — con quién se corresponde más (clientes, universidades, etc.).

En bases **muy grandes**, un barrido completo de todos los `From` tarda mucho. Use muestreo.

Alcance y límites (ventas vs menciones): **[REPORT_SCOPE_CLIENT.md](REPORT_SCOPE_CLIENT.md)** — copia en cada carpeta de informe como `ALCANCE_INFORME.md`.

**GPU:** Solo la fase **embeddings** usa CUDA. El escaneo SQL y el muestreo de dominios son CPU/SQLite. Si pide `--embeddings-sample`, esa fase corre **antes** del barrido de dominios para que la GPU no quede ociosa detrás de 400k filas en Python. Si sale `cuda available: False`, use `uv sync --group ml` y el índice CUDA de PyTorch del README (`python scripts/tools/check_torch_cuda.py`).

## Comandos

```bash
# Rápido: solo totales, año, clasificación y equipos (sin tablas de dominios)
uv run python scripts/reports/generate_client_report.py --fast --name resumen_2025

# Dominios sobre muestra de 400k mensajes (recomendado en DB grande)
uv run python scripts/reports/generate_client_report.py --domain-sample 400000 --name full_mar2025

# Todo el archivo para dominios (puede ser lento)
uv run python scripts/reports/generate_client_report.py --name dominios_completos

# + muestra embeddings (requiere uv sync --group ml)
uv run python scripts/reports/generate_client_report.py --domain-sample 300000 \
  --embeddings-sample 1200 --embeddings-clusters 12 --name con_clusters
```

## Embeddings aparte (más clusters / otro filtro)

```bash
RUN=~/data/origenlab-email/reports/20250314_120000_mi_run
uv run python scripts/ml/explore_email_clusters.py --limit 2000 --filter-any --n-clusters 14 --report-dir "$RUN"
# → escribe explore_clusters.json en esa carpeta
```

## Variable de entorno

`ORIGENLAB_REPORTS_DIR` — carpeta raíz de informes (compartir con el cliente vía zip o enlace).
