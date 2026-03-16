# Ubicaciones del archivo de correo (OrigenLab / LabDelivery)

Rutas del proyecto de análisis de correo. **No** forma parte del build del sitio; solo referencia para scripts e importación.

---

## Raíz del proyecto (WSL/Linux)

- **Carpeta base:** `/home/rafael/data/origenlab-email/`
- **SQLite:** `/home/rafael/data/origenlab-email/sqlite/emails.sqlite`
- **Informes:** `/home/rafael/data/origenlab-email/reports/`

---

## Raíz en Explorador de Windows

En la barra de direcciones del Explorador:

```
\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email
```

*(Si la distro WSL no es "Ubuntu", sustituir por el nombre correcto.)*

---

## Archivos PST (raw)

Carpeta en Windows:

```
\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\
```

PST conocidos en esa carpeta:

| Archivo | Ruta completa (Windows) |
|---------|--------------------------|
| backup.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup.pst` |
| backup1.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup1.pst` |
| backup2.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup2.pst` |
| backup3.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup3.pst` |
| backup4.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup4.pst` |
| backup24.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backup24.pst` |
| backuplast.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\backuplast.pst` |
| contacto@labdelivery.cl.pst | `\\wsl.localhost\Ubuntu\home\rafael\data\origenlab-email\raw_pst\contacto@labdelivery.cl.pst` |

Ruta en Linux (para scripts): `/home/rafael/data/origenlab-email/raw_pst/<nombre>.pst`

---

## Qué ejecutar para combinar y revisar (nuevos PST)

Los scripts de importación y reportes **no están en este repo** (origenlab-web). Están en el **proyecto de análisis de correo** (por ejemplo donde usas `uv run python scripts/...`).

Orden típico después de copiar nuevos PST en `raw_pst/`:

1. **Convertir PST → mbox** (si el pipeline lo hace por separado)  
   Ejecutar el script que lee de `raw_pst/` y escribe en `mbox/`. Incluir los nuevos: `backuplast.pst`, `backup24.pst`.

2. ** (Re)construir SQLite**  
   Ejecutar el script que lee todos los mbox en `mbox/` y llena (o actualiza) `sqlite/emails.sqlite`. Así los nuevos correos quedan combinados en la misma base.

3. **Comprobar**  
   Abrir la base o ejecutar un reporte de prueba para ver que el volumen/timeline reflejan los nuevos archivos.

4. **Generar informe cliente**  
   Desde ese mismo proyecto, por ejemplo:
   ```bash
   uv run python scripts/generate_client_report.py --fast --name cliente_mar2025
   ```
   O con muestra de dominios si la base es grande:
   ```bash
   uv run python scripts/generate_client_report.py --domain-sample 500000 --name cliente_full
   ```

**Dónde correr:** en el directorio del proyecto que contiene `scripts/generate_client_report.py` (y los scripts de PST→mbox y mbox→SQLite). Las rutas en este doc apuntan a los **datos** en `~/data/origenlab-email/`; el **código** puede estar en otro repo o carpeta.

---

*Actualizar la tabla de PST al añadir nuevos en `raw_pst/`.*
