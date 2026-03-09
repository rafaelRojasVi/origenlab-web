/**
 * Configuración central del sitio OrigenLab.
 * Usar para meta, footer, enlaces de contacto y texto compartido.
 */
export const site = {
  name: 'OrigenLab',
  domain: 'origenlab.cl',
  email: 'contacto@origenlab.cl',
  location: 'Valdivia, Chile',
  tagline: 'Equipamiento y soluciones para laboratorio',
  description:
    'OrigenLab — equipamiento y soluciones para laboratorio en Valdivia, Chile. Instrumentación, reactivos y asesoría técnica.',
  /** Placeholder: agregar número real cuando esté disponible */
  phone: '' as string,
  /** Placeholder: agregar número con código de país (ej. +56912345678) cuando esté disponible */
  whatsapp: '' as string,
  nav: [
    { href: '/nosotros', label: 'Nosotros' },
    { href: '/productos', label: 'Productos' },
    { href: '/marcas', label: 'Marcas' },
    { href: '/contacto', label: 'Contacto' },
  ] as const,
} as const;
