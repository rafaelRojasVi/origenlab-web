# OrigenLab — Sitio web

Sitio estático para **OrigenLab**, empresa de equipamiento y soluciones para laboratorio (Valdivia, Chile).  
Tech: Astro + Tailwind CSS. Contenido en español.

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

El build genera archivos estáticos en `dist/`. Para HostGator (hosting compartido):

1. Ejecutar `npm run build`.
2. Subir **todo el contenido** de `dist/` al directorio público del dominio (p. ej. `public_html` o la raíz del sitio para `origenlab.cl`), vía FTP o administrador de archivos (cPanel).
3. Asegurar que `index.html` esté en la raíz y que las rutas funcionen (HostGator suele servir `index.html` en carpetas; si no, ver `docs/deployment.md`).

Detalles: [docs/deployment.md](docs/deployment.md).

## Estructura relevante

- `src/config/site.ts` — Configuración central (nombre, email, dominio, etc.).
- `src/layouts/Layout.astro` — Layout principal (español, meta, header/footer).
- `src/pages/` — Páginas (index, nosotros, productos, marcas, contacto).
- `src/components/` — Header, Footer, Hero, CtaSection.
- `src/data/` — Datos de categorías y marcas (placeholders).
- `src/styles/global.css` — Estilos globales y Tailwind.

Contacto del sitio: **contacto@origenlab.cl**
