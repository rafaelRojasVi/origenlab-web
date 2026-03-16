/**
 * Datos de contacto únicos — usar en sitio y componentes.
 */
export const contact = {
  email: 'contacto@origenlab.cl',
  phoneDisplay: '+56 9 6256 7816',
  /** Sin espacios ni + para wa.me / tel */
  phoneE164: '56962567816',
  whatsappE164: '56962567816',
  /** Calle completa: no mostrar en el sitio público; solo referencia interna/AGENTS */
  addressLine: 'Oettinger 51, depto 206',
  city: 'Valdivia',
  country: 'Chile',
  /** Texto único para web (sin dirección de calle) */
  locationPublic: 'Valdivia, Chile' as const,
  hours: '09:00–18:00',
  /** Placeholder hasta tener handle en repo */
  instagramHandle: null as string | null,
} as const;

export function whatsappUrl(): string {
  return `https://wa.me/${contact.whatsappE164}`;
}

export function telUrl(): string {
  return `tel:+${contact.phoneE164}`;
}
