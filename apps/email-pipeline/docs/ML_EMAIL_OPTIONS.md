# ML sobre archivo de correo — qué tiene sentido

## No supervisado (lo que ya encaja sin etiquetas)

| Técnica | Qué hace | En este repo |
|--------|----------|--------------|
| **Embeddings + clustering** | Agrupa correos por “tema” semántico | `explore_email_clusters.py`, `generate_client_report.py` (MiniLM + agglomerative / k-means) |
| **K-Means** | Particiones esféricas, rápido, hay que elegir *k* | `email_ml_explore.py` |
| **Clustering jerárquico** | Árbol de fusión, interpretable por tamaño de cluster | Ya usado (cosine + average linkage) |
| **HDBSCAN** | Clusters por densidad, puede dejar ruido como “-1” | Opcional (`pip install hdbscan`), script lo intenta |
| **Topic modeling (LDA)** | Temas por palabras (bolsa de palabras) | Posible; peor con HTML/ruido que embeddings |
| **BERTopic** | Temas con embeddings + HDBSCAN | Pesado; bueno si quieres etiquetas automáticas por tema |

## Supervisado (hace falta etiquetas)

| Técnica | Necesitas | Uso típico |
|--------|-----------|------------|
| **Clasificador (logistic, XGB, small NN)** | Cientos/miles de mails etiquetados (cotización / spam / OC…) | Priorizar bandeja |
| **Detección de modelo de equipo** | Regex/catálogo **o** NER entrenado en fichas técnicas | Extraer “SB900”, “Adventurer AX…” |

Sin etiquetas reales, el supervisado se reduce a **pseudo-etiquetas** (palabras clave) → sesgo fuerte; útil solo como experimento.

## Incluir **modelo de maquinaria** si aparece en el texto

1. **Catálogo + regex (recomendado para empezar)**  
   Marcas que ya salen en tu informe (Ohaus, Steinlite, etc.) + patrones de modelo (`SB\d+`, nombres de serie).  
   → Script **`email_ml_explore.py`** lleva un bloque editable `EQUIPMENT_MODEL_PATTERNS`; cuenta menciones en subject+body.

2. **Ampliar el catálogo**  
   PDFs/catálogos del fabricante → lista de modelos → más regex o lista fija.

3. **NER / LLM**  
   Más flexible pero costoso y variable; el prompt de negocio (`EMAIL_BUSINESS_SIGNAL_PROMPT.md`) puede pedir “modelo si consta”.

## Comando rápido

```bash
uv sync --group ml
uv run python scripts/ml/email_ml_explore.py --limit 4000 --kmeans 16
# Salida: clusters + top modelos detectados por regex → JSON en stdout o --out
```

La GPU acelera solo la parte **embeddings**; clustering (sklearn) es CPU.
