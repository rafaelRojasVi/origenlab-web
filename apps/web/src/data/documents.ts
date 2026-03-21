/**
 * Modelo mínimo para futuros catálogos / fichas técnicas en el sitio.
 * No incluir entradas reales hasta exista archivo y permiso de publicación.
 *
 * Flujo recomendado cuando haya PDFs:
 * 1. Colocar archivo en public/documentos/<slug>.pdf (o URL externa estable).
 * 2. Añadir entrada en `documents` con fileUrl, kind, categorySlug si aplica.
 * 3. Listar en página de categoría con: documentsForCategory(cat.slug)
 *    o en una página /documentos si se prefiere índice global.
 */
export type DocumentKind = 'catalog' | 'datasheet' | 'other';

export interface SiteDocument {
  id: string;
  title: string;
  slug: string;
  kind: DocumentKind;
  /** Ruta bajo public/ (ej. /documentos/foo.pdf) o URL absoluta */
  fileUrl?: string;
  /** Opcional: asociar a slug de categoría en categories.ts */
  categorySlug?: string;
  notes?: string;
}

/** Vacío hasta cargar documentos reales. */
export const documents: SiteDocument[] = [];

/** Entradas publicables asociadas a una categoría (vacío mientras no haya datos). */
export function documentsForCategory(categorySlug: string): SiteDocument[] {
  return documents.filter((d) => d.categorySlug === categorySlug);
}
