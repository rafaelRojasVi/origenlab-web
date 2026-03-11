/**
 * Product categories – placeholder data for future extension.
 * Used by productos and categorías pages.
 */
export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

export const categories: Category[] = [
  { id: '1', name: 'Instrumentación', slug: 'instrumentacion', description: 'Equipos de medición, análisis y control de calidad para laboratorio.' },
  { id: '2', name: 'Reactivos y consumibles', slug: 'reactivos-consumibles', description: 'Reactivos, material de laboratorio y consumibles para sus ensayos.' },
  { id: '3', name: 'Equipos de laboratorio', slug: 'equipos-laboratorio', description: 'Mobiliario, equipos generales y accesorios para laboratorio.' },
];
