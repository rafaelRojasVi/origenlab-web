"""Explainable lead scoring. Deterministic and testable."""

from __future__ import annotations

# Max points per factor
SOURCE_STRENGTH_MAX = 2.0
PROCUREMENT_INTENT_MAX = 2.0
RESEARCH_LAB_MAX = 2.0
EQUIPMENT_MATCH_MAX = 2.0
CONTACT_INFO_MAX = 1.0
LAB_CONTEXT_MAX = 2.0
BUYER_KIND_MAX = 1.0


def score_source_strength(source_type: str | None) -> float:
    """Source credibility: procurement=2, accredited_lab=1.5, research_center=1."""
    if not source_type:
        return 0.0
    t = source_type.lower().strip()
    if t == "procurement":
        return 2.0
    if t == "accredited_lab":
        return 1.5
    if t == "research_center":
        return 1.0
    return 0.5


def score_procurement_intent(lead_type: str | None, source_type: str | None) -> float:
    """Active tender with equipment intent = 2; else 0 for non-procurement."""
    if source_type and source_type.lower() == "procurement" and lead_type and "tender" in lead_type.lower():
        return 2.0
    return 0.0


def score_research_lab_relevance(lead_type: str | None, source_type: str | None) -> float:
    """Accredited lab or CORFO center = 1.5-2."""
    if not lead_type and not source_type:
        return 0.0
    lt = (lead_type or "").lower()
    st = (source_type or "").lower()
    if "accredited_lab" in lt or st == "accredited_lab":
        return 2.0
    if "corfo" in lt or "center" in lt or st == "research_center":
        return 1.5
    return 0.0


def score_equipment_match(equipment_match_tags: str | None) -> float:
    """Equipment tags: 1 tag = 0.5, 2+ = 2 (cap at 2)."""
    if not equipment_match_tags or not equipment_match_tags.strip():
        return 0.0
    tags = [t.strip() for t in equipment_match_tags.split(",") if t.strip()]
    if not tags:
        return 0.0
    if len(tags) >= 2:
        return min(2.0, EQUIPMENT_MATCH_MAX)
    return 0.5


def score_contact_info(email: str | None, phone: str | None) -> float:
    """Has email or phone = 1."""
    if (email and email.strip()) or (phone and phone.strip()):
        return 1.0
    return 0.0


def score_lab_context(lab_context_score: float | None) -> float:
    """Lab/procurement context (0–2). Stored from normalization; capped here."""
    if lab_context_score is None:
        return 0.0
    try:
        v = float(lab_context_score)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(LAB_CONTEXT_MAX, v))


def score_buyer_kind(buyer_kind: str | None, *, source_type: str | None) -> float:
    """Small bonus (0–1) for buyer categories that usually have labs/equipment demand."""
    if not buyer_kind or not source_type or source_type.lower() != "procurement":
        return 0.0
    bk = buyer_kind.lower().strip()
    if bk in ("hospital", "universidad"):
        return 1.0
    if bk in ("agricola", "gobierno"):
        return 0.7
    if bk in ("municipal", "publico"):
        return 0.3
    return 0.0


def compute_priority_score(
    source_type: str | None,
    lead_type: str | None,
    equipment_match_tags: str | None,
    lab_context_score: float | None,
    buyer_kind: str | None,
    email: str | None,
    phone: str | None,
) -> tuple[float, str]:
    """Compute priority_score (0-10+) and a short priority_reason. Deterministic."""
    s1 = score_source_strength(source_type)
    s2 = score_procurement_intent(lead_type, source_type)
    s3 = score_research_lab_relevance(lead_type, source_type)
    s4 = score_equipment_match(equipment_match_tags)
    s5 = score_lab_context(lab_context_score)
    s6 = score_buyer_kind(buyer_kind, source_type=source_type)
    s7 = score_contact_info(email, phone)
    total = s1 + s2 + s3 + s4 + s5 + s6 + s7
    parts = []
    if s1 > 0:
        parts.append(f"fuente={s1:.1f}")
    if s2 > 0:
        parts.append(f"licitación={s2:.1f}")
    if s3 > 0:
        parts.append(f"lab/centro={s3:.1f}")
    if s4 > 0:
        parts.append(f"equipo={s4:.1f}")
    if s5 > 0:
        parts.append(f"contexto_lab={s5:.1f}")
    if s6 > 0:
        parts.append(f"buyer={s6:.1f}")
    if s7 > 0:
        parts.append("contacto")
    reason = "; ".join(parts) if parts else "sin señales"
    return round(total, 2), reason


def fit_bucket(
    *,
    priority_score: float,
    equipment_match_tags: str | None,
    lab_context_score: float | None,
    buyer_kind: str | None,
) -> str:
    """Simple review classification: high_fit / medium_fit / low_fit."""
    eq = score_equipment_match(equipment_match_tags)
    lab = score_lab_context(lab_context_score)
    bk = (buyer_kind or "").lower().strip()
    strong_buyer = bk in ("hospital", "universidad", "agricola")

    if eq >= 0.5 and (lab >= 0.8 or strong_buyer) and priority_score >= 6.0:
        return "high_fit"
    if eq >= 0.5 and (lab >= 0.6 or strong_buyer):
        return "high_fit"
    if lab >= 1.0 or strong_buyer:
        return "medium_fit"
    if eq >= 0.5:
        return "medium_fit"
    return "low_fit"
