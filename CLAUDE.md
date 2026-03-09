# OrigenLab — Instrucciones para asistencia con IA

## Contexto del proyecto

- **Cliente:** OrigenLab — empresa de equipamiento y soluciones para laboratorio (Valdivia, Chile).
- **Dominio:** origenlab.cl
- **Email público:** contacto@origenlab.cl (usar siempre este en el sitio).
- **Stack:** Astro + Tailwind CSS. Sitio estático, sin backend.
- **Idioma:** Español primero. Contenido profesional y orientado a laboratorios/científico.

## Reglas

- Mantener el sitio **estático**: sin API propia, sin base de datos, sin formularios que envíen a un backend. Contacto vía `mailto:contacto@origenlab.cl`.
- No inventar certificaciones, premios ni datos de la empresa que no estén confirmados.
- Reutilizar la configuración central en `src/config/site.ts` para nombre, email, dominio, ubicación, etc.
- Preferir componentes en `src/components/` y el layout en `src/layouts/Layout.astro`; evitar duplicar header/footer/meta.
- No añadir React ni otros frameworks de UI salvo que se pida explícitamente.
- Código legible para desarrolladores junior a mid-level.

## Rutas y estructura

- **Páginas:** `src/pages/` (index, nosotros, productos, marcas, contacto; categorías en `src/pages/categorias/[slug].astro`).
- **Datos:** `src/data/` (categorías, marcas) para contenido reutilizable.
- **Config:** `src/config/site.ts` para todo lo que sea nombre, email, dominio, tagline, descripción.
- **Estilos:** `src/styles/global.css` (Tailwind); mantener diseño sobrio y profesional.

## Build y despliegue

- Build: `npm run build` → salida en `dist/`.
- Despliegue: subir contenido de `dist/` al hosting (HostGator). Ver `docs/deployment.md`.
