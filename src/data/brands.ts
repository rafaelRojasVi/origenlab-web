/**
 * Brands / marcas – placeholder data for future extension.
 * Used by marcas page and product associations.
 */
export interface Brand {
  id: string;
  name: string;
  slug: string;
  url?: string;
}

export const brands: Brand[] = [
  { id: '1', name: 'Marcas disponibles', slug: 'marcas-disponibles' },
  { id: '2', name: 'Catálogo en actualización', slug: 'catalogo-actualizacion' },
];
