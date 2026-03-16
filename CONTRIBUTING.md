# Guía para colaboradores (y uso con Claude / Cursor)

Este repo es **un solo proyecto**: un sitio estático Astro para OrigenLab (Chile). No es un monorepo con varios paquetes; todo el código del sitio vive aquí, con documentación y reglas para que tanto personas como asistentes IA (Claude, Cursor) sigan las mismas fuentes de verdad.

---

## Por dónde empezar

| Si quieres… | Abre |
|-------------|------|
| **Entender el proyecto y correr el sitio** | [README.md](README.md) |
| **Reglas de negocio, datos y qué no inventar** | [AGENTS.md](AGENTS.md) |
| **Rutas rápidas para IA (qué archivo leer según la tarea)** | [CLAUDE.md](CLAUDE.md) |
| **Alcance de la empresa, contacto, tono y prompt para cotizaciones** | [docs/company-scope.md](docs/company-scope.md) |
| **Desplegar a HostGator** | [docs/deployment.md](docs/deployment.md) |

---

## Estructura del repo (una sola app)

```
origenlab-web/
├── src/                    # Código del sitio Astro
│   ├── data/               # Fuente de verdad: company, contact, categories, services, etc.
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── config/
│   └── styles/
├── public/                 # Assets estáticos (favicon, .htaccess, robots, sitemap)
├── docs/                   # Documentación (deploy, seguridad, alcance, email)
├── .cursor/rules/          # Reglas para Cursor (siempre aplicadas en este repo)
├── .claude/skills/         # Skills para Claude (deploy, copy, etc.)
├── AGENTS.md               # Instrucciones para agentes IA (reglas, datos, tono)
├── CLAUDE.md               # Router rápido para Claude
└── CONTRIBUTING.md         # Este archivo
```

Los datos de negocio (empresa, contacto, categorías, servicios) están en **`src/data/*.ts`**. No duplicar en el código; usar esos módulos. Para copy y cotizaciones, el resumen está en **`docs/company-scope.md`**.

---

## Uso con Claude (Cursor / API)

- **CLAUDE.md** indica qué archivo leer según la necesidad (datos, deploy, seguridad).
- **AGENTS.md** es la referencia completa: negocio, contacto, reglas de contenido, tono, despliegue.
- **Skills** en `.claude/skills/` se usan para tareas concretas:
  - `astro-hostgator-deploy`: revisar build y subida a HostGator.
  - `brand-copy`: redacción de páginas y CTAs alineada a la marca.
- **docs/company-scope.md** incluye el prompt listo para reescribir cotizaciones con otra IA (p. ej. ChatGPT).

No inventar marcas, certificaciones, plazos ni garantías no documentadas en `src/data/` o en `docs/`.

---

## Uso con Cursor

Las reglas en **`.cursor/rules/`** se aplican automáticamente en este workspace:

- **project.mdc** — Reglas de negocio, tono, datos y calidad de código (siempre activas).
- **astro-deploy.mdc** — Build, `dist/` y despliegue estático (se activa con archivos de Astro/public).
- **marketing-pages.mdc** — Páginas de contenido y copy (se activa con las rutas correspondientes).

Al abrir el repo en Cursor, esas reglas ya orientan las respuestas hacia los datos en `src/data/` y la documentación en `docs/`.

---

## Resumen para revisión de código

- **Datos:** Cambios a texto de negocio/contacto/categorías → hacerlos en `src/data/*`, no hardcodear en componentes.
- **Copy:** Tono profesional, español Chile, sin hype; CTAs tipo «Solicitar cotización», «Contactar por WhatsApp».
- **Deploy:** Build con `npm run build`; subir el **contenido** de `dist/` (no la carpeta `dist`) al directorio público en HostGator; incluir `.htaccess`.
- **Seguridad/claims:** Antes de añadir enlaces o afirmaciones de confianza, revisar [docs/security-audit-v1.md](docs/security-audit-v1.md).

Si algo no está documentado aquí, **AGENTS.md** y **docs/company-scope.md** son la siguiente parada.
