# Widget flotante WhatsApp — notas

## Implementación actual (patrón estable)

- **Componente:** `src/components/FloatingChat.astro`
- **Montaje:** al final de `body` en `Layout.astro` (hijo directo de `body`, fuera del footer).
- **Clases:** `.wa-widget`, `.wa-inner`, `.wa-card`, `.wa-btn`, `.wa-pulse--back` / `--front`, `.wa-icon`.
- **Desktop (hover):** solo se ve el botón; la tarjeta entra al pasar el mouse o al foco (`:focus-within`).
- **Touch:** `@media (hover: none)` — tarjeta siempre visible (no hay hover fiable).
- **Brillo:** animación vertical en sombra del botón (`wa-btn-glow`) + dos pulsos desfasados (`wa-pulse-up` / `wa-pulse-down`).

### Por qué no se corta

1. **Márgenes reales:** `right` / `bottom` = `max(1rem, env(safe-area-inset-*))`.
2. **Ancho del bloque:** `max-width: calc(100vw - 2rem)` para no pasarse del viewport.
3. **Tarjeta:** `min-width: 0`, `max-width: min(16rem, calc(100vw - botón - 3rem))` para que no empuje el botón.
4. **Pulso:** en un `<span class="wa-pulse">` detrás del botón (no escala el botón entero).
5. **Muy angosto (<320px):** columna (tarjeta arriba, botón abajo).
6. **Footer:** `padding-bottom` extra para que el contenido no quede bajo el widget.

### Si algo sigue raro

- Comprobar que ningún ancestro del widget tenga `transform`, `filter`, `contain: paint` o `overflow: hidden` (el widget ya está fuera del main/footer).
- `body` tiene `overflow-x: hidden` por el hero; el widget compensa con márgenes y `max-width`.

### Reducir movimiento

- `prefers-reduced-motion`: pulso más suave / menos animación.
