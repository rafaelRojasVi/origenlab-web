"""Helpers for enriching leads with product angle, outreach strategy, and site/domain guesses.

These helpers are deliberately conservative and only use information we already have
in the database (no web calls, no guessing of individual emails).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class LeadContext:
    source_name: str | None
    buyer_kind: str | None
    organization_type_guess: str | None
    equipment_match_tags: list[str]
    lab_context_tags: list[str]
    priority_score: float | None
    fit_bucket: str | None
    org_name: str | None


def _split_tags(s: str | None) -> list[str]:
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]


def _has_any(tags: Iterable[str], candidates: Iterable[str]) -> bool:
    s = {t.lower() for t in tags}
    return any(c.lower() in s for c in candidates)


def derive_product_angle(
    *,
    source_name: str | None,
    buyer_kind: str | None,
    organization_type_guess: str | None,
    equipment_match_tags: str | None,
    lab_context_tags: str | None,
    evidence_summary: str | None,
) -> tuple[str, str, str]:
    """Return (likely_product_angle, likely_equipment_interest, why_this_lead_matters).

    The goal is to produce short, conservative Spanish phrases that are helpful for sales,
    without inventing unsupported claims.
    """
    eq_tags = _split_tags(equipment_match_tags)
    lab_tags = _split_tags(lab_context_tags)
    ctx = LeadContext(
        source_name=(source_name or "").lower() or None,
        buyer_kind=(buyer_kind or "").lower() or None,
        organization_type_guess=(organization_type_guess or "").lower() or None,
        equipment_match_tags=eq_tags,
        lab_context_tags=lab_tags,
        priority_score=None,
        fit_bucket=None,
        org_name=None,
    )

    # Map equipment tags to human phrases.
    tag_to_phrase: dict[str, str] = {
        "balanza": "balanza analítica / control de calidad",
        "centrifuga": "centrífuga / separación de muestras",
        "microscopio": "microscopía y documentación",
        "phmetro": "medición de pH / análisis químico",
        "autoclave": "autoclaves y esterilización",
        "cromatografia_hplc": "HPLC / cromatografía líquida",
        "humedad_granos": "medición de humedad en granos",
    }

    equipment_interest = ""
    for tag in eq_tags:
        if tag in tag_to_phrase:
            equipment_interest = tag_to_phrase[tag]
            break

    # If no explicit equipment tag, fall back to lab context.
    if not equipment_interest and lab_tags:
        if _has_any(lab_tags, ["ambiental_agua_residuos"]):
            equipment_interest = "equipamiento para laboratorio ambiental / aguas"
        elif _has_any(lab_tags, ["alimentos"]):
            equipment_interest = "equipamiento para laboratorio de alimentos / inocuidad"
        elif _has_any(lab_tags, ["microbiologia"]):
            equipment_interest = "equipamiento para microbiología / bromatología"
        elif _has_any(lab_tags, ["analisis_quimico", "calibracion_metrologia"]):
            equipment_interest = "equipamiento para análisis químico / metrología"
        elif _has_any(lab_tags, ["investigacion_docencia"]):
            equipment_interest = "equipamiento para docencia / investigación"
        elif _has_any(lab_tags, ["laboratorio", "equipamiento_laboratorio"]):
            equipment_interest = "equipamiento general de laboratorio"

    # Product angle combines equipment with buyer type.
    product_angle = ""
    bk = ctx.buyer_kind or ""
    if equipment_interest:
        if bk == "hospital":
            product_angle = f"{equipment_interest} para laboratorio hospitalario"
        elif bk == "universidad":
            product_angle = f"{equipment_interest} para laboratorio universitario / docencia"
        elif bk == "agricola":
            product_angle = f"{equipment_interest} para laboratorio agrícola / SAG / agro"
        elif bk in ("gobierno", "municipal"):
            product_angle = f"{equipment_interest} para laboratorio o control de calidad institucional"
        else:
            product_angle = equipment_interest
    elif lab_tags:
        # We have lab context but no specific equipment.
        if bk == "hospital":
            product_angle = "equipamiento de laboratorio clínico / hospitalario"
        elif bk == "universidad":
            product_angle = "equipamiento para laboratorios universitarios / investigación"
        else:
            product_angle = "equipamiento de laboratorio / control de calidad"

    # Why this lead matters: short narrative using context and evidence.
    why = ""
    if equipment_interest and ctx.buyer_kind:
        why = f"Organismo {ctx.buyer_kind} con señales de {equipment_interest}."
    elif equipment_interest:
        why = f"Señales de interés en {equipment_interest}."
    elif lab_tags:
        why = "Señales de trabajo de laboratorio o análisis, aunque el equipo no está totalmente explícito."

    # Append trimmed evidence summary if available.
    evid = (evidence_summary or "").strip()
    if evid:
        short_evid = evid[:200]
        if why:
            why = f"{why} Ejemplo: {short_evid}"
        else:
            why = f"Ejemplo de contexto: {short_evid}"

    return product_angle, equipment_interest, why


def derive_outreach_strategy(
    *,
    source_name: str | None,
    buyer_kind: str | None,
    lead_type: str | None,
    equipment_match_tags: str | None,
    lab_context_tags: str | None,
) -> str:
    """Return a short Spanish outreach strategy description."""
    src = (source_name or "").lower()
    bk = (buyer_kind or "").lower()
    lt = (lead_type or "").lower()
    eq_tags = _split_tags(equipment_match_tags)
    lab_tags = _split_tags(lab_context_tags)

    from_chilecompra = src == "chilecompra" or "mercado" in src
    explicit_equipment = bool(eq_tags)
    strong_lab = bool(lab_tags)

    # Hospitals: compras first, tech second.
    if bk == "hospital":
        if explicit_equipment:
            return "Compras primero; hospital público con señal directa de equipamiento. Técnico de laboratorio como segundo paso."
        return "Compras primero; hospital público. Técnico de laboratorio/clínico como segundo paso si existe."

    # Universities and research centers: often technical first.
    if bk == "universidad":
        if explicit_equipment or strong_lab:
            return "Técnico primero (laboratorio / académico responsable); luego compras o abastecimiento central."
        return "Compras o abastecimiento universitario; luego contacto con laboratorio o académico si aplica."

    if bk == "agricola":
        return "Compras/abastecimiento primero; servicio agrícola con foco en laboratorio o control de calidad."

    if bk in ("gobierno", "municipal"):
        if from_chilecompra or lt == "tender_buyer":
            return "Compras/licitaciones primero; organismo público con licitación en ChileCompra. Transparencia/OIRS como respaldo."
        return "Compras o unidad de abastecimiento; transparencia/OIRS si no hay ruta directa."

    # Generic public buyer.
    if from_chilecompra or lt == "tender_buyer":
        if explicit_equipment:
            return "Compras primero; licitación con equipo explícito. Considerar contacto técnico si se identifica laboratorio específico."
        if strong_lab:
            return "Compras/licitaciones primero; licitación con señales de laboratorio. Técnico como segundo paso."
        return "Compras/licitaciones; licitación genérica. Transparencia/OIRS como ruta de respaldo."

    # Labs / centers from INN or CORFO.
    if src in ("inn_labs", "inn", "corfo_centers", "corfo"):
        if explicit_equipment or strong_lab:
            return "Técnico o jefe de laboratorio primero; luego compras o abastecimiento si es necesario."
        return "Contacto general del centro; luego identificar laboratorio o área técnica relevante."

    # Fallback.
    return "Contacto general primero; luego identificar compras o laboratorio según la respuesta."


def guess_official_site_and_domain(
    *,
    lead_website: str | None,
    lead_domain: str | None,
    match_domain: str | None,
) -> tuple[str | None, str | None]:
    """Return a conservative (official_site_guess, official_domain_guess).

    Rules:
    - Never return mercadopublico.cl as buyer domain.
    - Prefer explicit lead website/domain when present.
    - Then prefer matched mart domain when present.
    - Otherwise return (None, None).
    """
    def _clean(s: str | None) -> str | None:
        if not s:
            return None
        s = s.strip()
        return s or None

    def _is_marketplace_domain(d: str | None) -> bool:
        if not d:
            return False
        d_l = d.lower()
        return "mercadopublico.cl" in d_l or "chilecompra.cl" in d_l

    website = _clean(lead_website)
    domain = _clean(lead_domain)

    # Normalize obvious marketplace domains away.
    if domain and _is_marketplace_domain(domain):
        domain = None
    if website and "mercadopublico.cl" in website.lower():
        website = None

    # 1) Prefer explicit lead domain if not marketplace.
    if domain:
        if not website:
            website = f"https://{domain}"
        return website, domain

    # 2) Use website if it clearly looks like an institutional site.
    if website:
        # Do not try to parse or guess domain aggressively; just reuse what we see.
        return website, None

    # 3) Fallback to matched mart domain if safe.
    mdom = _clean(match_domain)
    if mdom and not _is_marketplace_domain(mdom):
        return f"https://{mdom}", mdom

    return None, None

