"""Equipment keyword/tag matching for leads. Reuses mart tag set; adds procurement Spanish phrases."""

from __future__ import annotations

import re

from origenlab_email_pipeline.business_mart import equipment_tags_from_text

# Additional Spanish procurement/public-source phrases that map to the same tag names as the mart.
# Each tuple: (tag_name, pattern). Tag names must match business_mart's _EQUIPMENT_PATTERNS.
_LEADS_EXTRA_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("balanza", re.compile(r"balanza anal[ií]tica|balanza de precisi[oó]n|balanza industrial|balanza granataria|b[aá]scula|calibraci[oó]n balanza", re.I)),
    ("centrifuga", re.compile(r"centr[ií]fuga refrigerada|microcentr[ií]fuga|ultracentr[ií]fuga|rotor|tubos falcon", re.I)),
    ("cromatografia_hplc", re.compile(r"cromatograf[ií]a l[ií]quida|cromat[oó]grafo|detector UV|columna HPLC|bomba HPLC", re.I)),
    ("autoclave", re.compile(r"esterilizador|esterilizaci[oó]n|vapor|bioseguridad", re.I)),
    ("microscopio", re.compile(r"microscop[ií]a|lupa estereosc[oó]pica|objetivos|c[aá]mara microscopio", re.I)),
    ("phmetro", re.compile(r"ph-metro|medidor pH|conduct[ií]metro|turbid[ií]metro|calidad de agua", re.I)),
    ("humedad_granos", re.compile(r"humedad granos|medidor de humedad|analizador de humedad|secado|trigo|ma[ií]z", re.I)),
]


def equipment_tags_for_leads(text: str) -> list[str]:
    """Return equipment tags from text. Uses mart tags plus procurement Spanish phrases.
    Tag names match business_mart so lead_master.equipment_match_tags aligns with mart.
    """
    if not text:
        return []
    tags: set[str] = set()
    # Reuse mart's equipment_tags_from_text (same tag set).
    for t in equipment_tags_from_text(text):
        tags.add(t)
    # Add leads-specific Spanish phrases mapped to same tags.
    for tag, pat in _LEADS_EXTRA_PATTERNS:
        if pat.search(text):
            tags.add(tag)
    return sorted(tags)


# Lab/procurement relevance phrases (separate from equipment tags).
# Goal: detect that a tender is about lab/scientific work even if it doesn't mention a specific instrument.
_LAB_CONTEXT_PATTERNS: list[tuple[str, re.Pattern[str], float]] = [
    ("laboratorio", re.compile(r"\blaboratorio\b|\blab\.?\b", re.I), 1.0),
    ("laboratorio_clinico", re.compile(r"laboratorio\s+cl[ií]nico|cl[ií]nica\s+laboratorio", re.I), 1.0),
    ("analisis_quimico", re.compile(r"an[aá]lisis\s+qu[ií]mico|qu[ií]mica\s+anal[ií]tica|instrumentaci[oó]n", re.I), 0.8),
    ("microbiologia", re.compile(r"microbiolog[ií]a|bromatolog[ií]a", re.I), 0.8),
    ("control_calidad", re.compile(r"control\s+de\s+calidad|aseguramiento\s+de\s+calidad", re.I), 0.6),
    ("calibracion_metrologia", re.compile(r"calibraci[oó]n|metrolog[ií]a", re.I), 0.6),
    ("ensayo_medicion_muestras", re.compile(r"ensayo(s)?|medici[oó]n|muestra(s)?", re.I), 0.4),
    ("ambiental_agua_residuos", re.compile(r"laboratorio\s+ambiental|agua(s)?\s+y\s+residuo(s)?|residuo(s)?\s+peligroso(s)?", re.I), 0.8),
    ("alimentos", re.compile(r"laboratorio\s+de\s+alimento(s)?|inocuidad|alimento(s)?", re.I), 0.6),
    ("investigacion_docencia", re.compile(r"investigaci[oó]n|docencia|biotecnolog[ií]a|qu[ií]mica", re.I), 0.6),
    ("equipamiento_laboratorio", re.compile(r"equipamiento\s+de\s+laboratorio|equipamiento\s+cient[ií]fico|equipamiento\s+t[eé]cnico", re.I), 0.7),
]


def lab_context_signals(text: str) -> tuple[float, list[str]]:
    """Return (lab_context_score, signal_tags).

    Score is capped at 2.0. This is intended to capture lab/scientific procurement context even
    when there is no explicit equipment tag.
    """
    if not text or not text.strip():
        return 0.0, []
    tags: list[str] = []
    score = 0.0
    for tag, pat, w in _LAB_CONTEXT_PATTERNS:
        if pat.search(text):
            tags.append(tag)
            score += float(w)
    # Do not overcount generic procurement language: require at least one strong signal
    # (laboratorio/equipamiento_laboratorio/clinical/microbiologia/etc.) to exceed 0.6.
    score = min(2.0, score)
    return round(score, 2), tags
