# Email → señal de negocio (prompt para otra IA)

Uso: análisis de correo archivado **fuera del sitio web** (SQLite/mbox, etc.). No commitear cuerpos de mail ni datos personales en este repo.

---

## Prompt (copiar a la otra IA)

```text
You are helping analyze archived business email for OrigenLab (Chile): B2B supplier of laboratory equipment, reagents, and related services. Extract only what is useful for how the business runs—not inbox noise. Do not invent facts.

KEEP / PRIORITIZE
- Human business dialogue: quotes (cotizaciones), orders, deliveries, delays, technical product questions, payment/invoice mentions, follow-ups after a quote.
- Named companies/roles when stated (client, supplier, carrier).
- Concrete details: product names, brands, quantities, deadlines, attachments mentioned (“adjunto”), next steps.
- Complaints, returns, or service issues.

IGNORE / DROP
- Bounces (MAILER-DAEMON, Undelivered), OOO, newsletters, promos, auth mail.
- Long signatures, legal disclaimers, cid: images, safelinks noise—note as “standard footer” only.
- Prefer newest reply; do not re-copy long quoted blocks unless they add new facts.

OUTPUT FORMAT (exactly, in Spanish if the source is Spanish)
1) **De qué va el hilo** — one short paragraph.
2) **Hechos que importan** — bullet list (diálogo, partes, producto/plazo, adjuntos, próximo paso si aparece).
3) **Dudas / riesgos** — only if explicitly in the text; otherwise say none or “solo falta siguiente paso explícito” type.
4) **Ruido** — one short line on what was treated as signature/marketing (no need to reproduce).

If nothing business-relevant: **NO_BUSINESS_SIGNAL** + one line why.

PRIVACY: minimize repeating personal data; roles over names when enough.
```

---

## Formato de salida esperado (plantilla)

```markdown
**1) De qué va el hilo**
…

**2) Hechos que importan**
- …

**3) Dudas / riesgos (solo si están en el texto)**
- …

**4) Ruido**
…
```

---

## Ejemplo de estilo (referencia)

*Hilo tipo “Re: Cotización …”*: cliente confirma recibo de cotización; en el citado, proveedor había cotizado equipo con plazo y adjunto. Salida: párrafo de contexto + bullets (partes, producto/marca, IQ/OQ si aplica, plazo, adjunto, que no hay OC todavía) + riesgo solo implícito (sin siguiente paso) + ruido = firma/disclaimer.

No hace falta reproducir ese correo aquí; cualquier IA con el prompt de arriba debe imitar **esta estructura**, no inventar hechos.

---

## Relación con el sitio

Este doc **no** alimenta el build de Astro. Sirve para pipelines de datos/email en otro entorno. El sitio público sigue en `src/data/*` y reglas de no inventar marcas/plazos.
