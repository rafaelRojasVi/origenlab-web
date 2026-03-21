# Informes, `active/` y paquete cliente (leads)

## Fuente de verdad

- **SQLite** (`ORIGENLAB_SQLITE_PATH`, p. ej. `~/data/origenlab-email/sqlite/emails.sqlite`) es el registro maestro: `lead_master`, `external_leads_raw`, `lead_matches_existing_orgs`, `lead_outreach_enrichment`, y el mart de correo (`organization_master`, `contact_master`, …).
- Ningún CSV sustituye a la base; los CSV son **vistas exportadas** o **hojas de trabajo** que pueden quedar desalineadas si no se regeneran.

## Carpetas bajo `reports/out/`

| Ubicación | Propósito |
|-----------|-----------|
| **`reports/out/active/`** | Archivos operativos **mínimos**: foco semanal, resumen MD, hoja de hunting actual, opcional `for_deepsearch`. Al ejecutar `prepare_active_workspace.py`, otros CSV en esta carpeta se mueven a `archive/`. |
| **`reports/out/client_pack_latest/`** | **Entregable cliente**: informe estático (HTML + MD + JSON + anexo CSV). Regenerar con el script de build; puede sobrescribirse en cada ejecución. |
| **`reports/out/archive/`** | Históricos, limpiezas, dumps grandes (`leads_export*.csv`, etc.). |
| **`reports/out/reference/`** | Experimentos y recortes (p. ej. Deep Research de prueba). |

## Hojas de cálculo vs informe principal

- El **informe principal** para el cliente debe ser el **paquete** (`index.html` + `resumen_ejecutivo_es.md`), no una carpeta de Excel sueltos.
- **`anexo_leads.csv`** es un anexo **técnico legible** con `id_lead` para trazabilidad con la base.
- La hoja **`leads_contact_hunt_current.csv`** es para **operaciones internas** (hunting); no es el entregable narrativo.

## Comandos útiles

```bash
# Paquete cliente (desde la raíz del repo)
uv run python scripts/reports/build_leads_client_pack.py

# Validar que merged y current comparten los mismos id_lead antes de importar
uv run python scripts/leads/validate_contact_hunt_alignment.py

# Limpiar active/ (archivar CSV que no son del núcleo)
uv run python scripts/leads/prepare_active_workspace.py
```

Más detalle del pipeline de leads: **[LEAD_PIPELINE.md](LEAD_PIPELINE.md)**. Auditoría amplia: **[PROJECT_AUDIT_AND_REPORTING_PLAN.md](PROJECT_AUDIT_AND_REPORTING_PLAN.md)**.
