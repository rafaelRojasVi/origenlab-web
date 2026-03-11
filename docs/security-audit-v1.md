# OrigenLab — Auditoría de seguridad y arquitectura v1

Auditoría enfocada para el sitio estático Astro desplegado en HostGator (sin backend).

---

## 1. Estructura del proyecto

**Estado: adecuada para un sitio brochure/catálogo de pequeña empresa.**

- **config**: `site.ts` centraliza nombre, dominio, email, navegación. Sin complejidad innecesaria.
- **data**: `categories.ts` y `brands.ts` son datos estáticos; fáciles de extender.
- **components**: Header, Footer, Hero, CtaSection, PageHeader, Card. Reutilización clara.
- **layouts**: Un solo layout (`Layout.astro`) con slot. Mantenible.
- **pages**: Rutas planas (index, nosotros, productos, marcas, contacto) + `categorias/[slug]`. Coherente con sitio estático.

No se detectó complejidad innecesaria en páginas, componentes ni datos.

---

## 2. Seguridad (despliegue estático)

### Revisado y correcto

- **Sin backend**: No hay API, formularios que envíen a servidor propio ni base de datos. Riesgo de inyección/autenticación en el propio sitio: nulo.
- **Sin secretos en código**: No hay `process.env` / `import.meta.env` en `src/`. `.env` y `.env.production` están en `.gitignore`.
- **Sin scripts externos**: No hay `<script src="http(s)://...">`, ni llamadas a terceros. Sin riesgo de mixed content ni dependencia de CDN no controlados.
- **Enlaces**: Todos los `href` son relativos (`/`, `/contacto`, etc.) o `mailto:contacto@origenlab.cl`. No hay redirecciones a dominios externos.
- **Redirect interno**: Solo `Astro.redirect('/productos')` cuando no existe la categoría; destino fijo y controlado.

### Sin problemas detectados

- **Recursos HTTP**: No se usa `http://` en assets ni enlaces. Favicon y CSS son rutas relativas; no hay mixed content.
- **Terceros**: No hay analytics, chat ni scripts de terceros en el código actual.

---

## 3. Favicon y meta

- **Favicon**: Presente en `public/favicon.svg` y referenciado en `Layout.astro` como `/favicon.svg`. Consistente en todas las páginas.
- **Meta**: Cada página define `title` y `description` vía el layout. `charset` UTF-8 y `viewport` correctos.
- **No implementado (opcional)**:
  - `canonical` para SEO.
  - `og:title`, `og:description`, `og:image` para redes sociales.
  - `theme-color` para navegador.

---

## 4. Cabeceras de seguridad y HTTPS

- **Antes de la auditoría**: No había orientación en el proyecto para HTTPS ni cabeceras de seguridad en HostGator.
- **Cambios realizados**:
  - Añadido `public/.htaccess` con:
    - Redirección HTTP → HTTPS (301).
    - Cabeceras: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`.
  - Actualizado `docs/deployment.md` con instrucciones para subir `.htaccess` y uso de HTTPS/cabeceras.

El `.htaccess` se copia a la raíz de `dist/` en el build; debe incluirse al subir los archivos al hosting (algunos clientes FTP ocultan archivos que empiezan por punto).

---

## 5. Información expuesta en HTML

- **Generator**: `<meta name="generator" content="Astro v5.x">` expone la versión de Astro. Riesgo bajo; opcional quitarlo o dejarlo genérico si se quiere reducir fingerprinting.

---

## 6. Enlaces y redirecciones

- Enlaces internos comprobados: `/`, `/nosotros`, `/productos`, `/marcas`, `/contacto`, `/categorias/:slug`. Todas las rutas existen en el build.
- Única redirección: categoría inexistente → `/productos`. Correcta y segura.

---

## Clasificación de hallazgos

### Debe corregirse antes del lanzamiento

| # | Hallazgo | Acción |
|---|----------|--------|
| 1 | No había refuerzo de HTTPS ni cabeceras de seguridad documentadas para HostGator. | **Hecho**: añadido `public/.htaccess` y sección en `docs/deployment.md`. Verificar al desplegar que `.htaccess` se sube y que HTTPS está activo en el dominio. |

No quedan ítems obligatorios pendientes para un lanzamiento estático básico.

---

### Conviene corregir pronto

| # | Hallazgo | Recomendación |
|---|----------|----------------|
| 1 | Al subir por FTP/cPanel, `.htaccess` puede no subirse si el cliente oculta archivos que empiezan por punto. | Incluir en checklist de despliegue: “Confirmar que `.htaccess` está en la raíz del sitio y que las visitas por HTTP redirigen a HTTPS”. |
| 2 | No hay meta canonical ni Open Graph. | Añadir en `Layout.astro` (o por página) `canonical` y, si interesa compartir en redes, `og:title`, `og:description` y opcionalmente `og:image` usando `site.domain`. |

---

### Mejoras posteriores (nice to have)

| # | Hallazgo | Sugerencia |
|---|----------|------------|
| 1 | El meta `generator` expone la versión de Astro. | Quitar la etiqueta o usar un valor genérico (`content="Astro"`) si se quiere reducir fingerprinting. |
| 2 | No hay política de contenido (CSP). | Para un sitio 100 % estático sin scripts externos, se puede añadir un CSP estricto en `.htaccess` (p. ej. `Content-Security-Policy: default-src 'self'`) en una fase posterior. |
| 3 | Favicon solo en SVG. | Añadir `favicon.ico` en `public/` y enlazarlo en el layout como fallback para navegadores antiguos. |

---

## Resumen

- **Arquitectura**: Adecuada y mantenible para un sitio brochure/catálogo estático; sin complejidad innecesaria.
- **Seguridad estática**: Sin secretos en código, sin scripts externos, sin mixed content ni redirecciones peligrosas.
- **Mejoras aplicadas**: `.htaccess` con HTTPS y cabeceras básicas; documentación de despliegue actualizada.
- **Próximos pasos recomendados**: Validar en producción que HTTPS y `.htaccess` funcionan; después, opcionalmente canonical/OG y CSP.
