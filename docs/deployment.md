# Despliegue — OrigenLab (HostGator)

Sitio estático generado con Astro. El resultado del build son HTML, CSS y assets en la carpeta `dist/`.

## Pasos

1. **Build local**
   ```bash
   npm run build
   ```
   La salida queda en `dist/`.

2. **Subir a HostGator**
   - Conectar por **FTP** o usar el **Administrador de archivos** en cPanel.
   - Subir **todo el contenido** de `dist/` al directorio público del dominio:
     - Si el sitio es la cuenta principal: suele ser `public_html`.
     - Si es un addon domain para `origenlab.cl`: la carpeta asignada a ese dominio (p. ej. `public_html/origenlab` o la raíz que indique HostGator).
   - La raíz del sitio debe contener `index.html` (página de inicio).

3. **URLs y carpetas**
   - Astro genera rutas como `productos/index.html`, `nosotros/index.html`, etc.
   - En HostGator, normalmente solicitar `/productos` sirve `productos/index.html`. Si no, puede ser necesario configurar reglas de reescritura (p. ej. `.htaccess`) para URLs limpias; en la mayoría de planes compartidos la configuración por defecto ya lo permite.

4. **Dominio y email**
   - Asegurar que el dominio **origenlab.cl** apunte al hosting (DNS configurado en el registrador).
   - El correo **contacto@origenlab.cl** se configura en HostGator (cPanel → Correo electrónico). No forma parte del build; es configuración del hosting.

## Resumen

| Acción        | Dónde / Cómo                          |
|---------------|----------------------------------------|
| Build         | `npm run build` → `dist/`             |
| Subir archivos| FTP o cPanel → directorio público     |
| Dominio       | DNS → servidor HostGator              |
| Email         | cPanel → Correo (contacto@origenlab.cl) |

No se requiere Node.js en el servidor; solo se sirven archivos estáticos.
