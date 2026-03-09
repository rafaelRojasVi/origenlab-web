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
  { id: '1', name: 'Instrumentación', slug: 'instrumentacion', description: 'Equipos de medición y análisis' },
  { id: '2', name: 'Reactivos y consumibles', slug: 'reactivos-consumibles', description: 'Reactivos y material de laboratorio' },
  { id: '3', name: 'Equipos de laboratorio', slug: 'equipos-laboratorio', description: 'Mobiliario y equipos generales' },
];
