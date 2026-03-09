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
  { id: '1', name: 'Marca ejemplo A', slug: 'marca-ejemplo-a' },
  { id: '2', name: 'Marca ejemplo B', slug: 'marca-ejemplo-b' },
  { id: '3', name: 'Marca ejemplo C', slug: 'marca-ejemplo-c' },
];
