/**
 * Marcas representadas — lista formal pendiente.
 * No inventar marcas; al confirmar, añadir entradas con name, slug y opcional url.
 */
export interface Brand {
  id: string;
  name: string;
  slug: string;
  url?: string;
}

/** Hasta tener marcas confirmadas, una sola entrada honesta evita claims falsos. */
export const brands: Brand[] = [
  {
    id: 'pending',
    name: 'Marcas en actualización',
    slug: 'marcas-en-actualizacion',
  },
];
