# OrigenLab — Sitio web

Sitio estático para **OrigenLab**, empresa de equipamiento y soluciones para laboratorio (Valdivia, Chile).  
**Stack:** Astro + Tailwind CSS. Contenido en español. Despliegue manual a HostGator (public_html).

**Alcance del negocio:** venta de equipos para laboratorios de servicio e investigación en Chile; líneas en alimentos, control de calidad y laboratorio clínico. Audiencia: laboratorios, universidades, clínicas, hospitales, I+D. Datos completos (contacto, servicios, tono, prompt para cotizaciones): [docs/company-scope.md](docs/company-scope.md). Código fuente de verdad: `src/data/*`.

## Comandos

| Comando | Descripción |
|---------|-------------|
| `npm install` | Instalar dependencias |
| `npm run dev` | Servidor de desarrollo en `http://localhost:4321` |
| `npm run build` | Build de producción → carpeta `dist/` |
| `npm run preview` | Vista previa del build local |
| `npm run check` | Verificación de tipos y contenido (Astro) |
| `npm run lint` | Mismo que `check` |

## Despliegue (HostGator)

1. `npm run check` y `npm run build`.
2. Subir **todo el contenido** de `dist/` a `public_html` (no una carpeta `dist` dentro de public_html).
3. Incluir el archivo `.htaccess` (HTTPS y cabeceras de seguridad).

Checklist completo y pasos: [docs/deployment.md](docs/deployment.md). Estado actual: [docs/deployment-status.md](docs/deployment-status.md).

## Estructura del proyecto

- `src/config/site.ts` — Configuración central (nombre, dominio, email, baseUrl, nav).
- `src/layouts/Layout.astro` — Layout principal (español, meta, canonical, Header/Footer).
- `src/pages/` — Inicio, nosotros, productos, marcas, contacto; categorías en `categorias/[slug].astro`.
- `src/components/` — Header, Footer, Hero, QuoteCTA, PageHeader, Card.
- `src/data/` — Categorías y marcas (datos estáticos).
- `src/styles/global.css` — Estilos globales y Tailwind.
- `public/.htaccess` — Se copia a `dist/`; forzar HTTPS y cabeceras básicas en el servidor.

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [docs/deployment.md](docs/deployment.md) | Pasos de despliegue y checklist antes del lanzamiento |
| [docs/deployment-status.md](docs/deployment-status.md) | Estado actual, hosting, DNS, advertencias |
| [docs/email-setup.md](docs/email-setup.md) | Email contacto@origenlab.cl (Titan, IMAP/SMTP, DKIM) |
| [docs/legacy-mail-migration-notes.md](docs/legacy-mail-migration-notes.md) | Notas sobre migración de correo legacy (LabDelivery; proyecto aparte) |
| [docs/company-scope.md](docs/company-scope.md) | Alcance, contacto, servicios, tono y prompt para redactar cotizaciones |
| [docs/email-archive-locations.md](docs/email-archive-locations.md) | Ubicaciones del archivo de correo (raw PST, SQLite, rutas Windows/WSL) |
| [docs/security-audit-v1.md](docs/security-audit-v1.md) | Auditoría de seguridad y arquitectura v1 |
| [CLAUDE.md](CLAUDE.md) | Instrucciones para asistencia con IA |

## Repo y ramas

- **GitHub:** repo remoto configurado.
- **Ramas:** `main`, `dev`. Desarrollo en `dev`.

**Contacto del sitio:** contacto@origenlab.cl
