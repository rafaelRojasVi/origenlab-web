"""Normalize raw lead records into lead_master fields. No scoring here."""

from __future__ import annotations

import json
import re
from typing import Any

from origenlab_email_pipeline.business_mart import domain_of, guess_org_type_from_domain
from origenlab_email_pipeline.leads_equipment import equipment_tags_for_leads, lab_context_signals
from origenlab_email_pipeline.leads_ingest import (
    SOURCE_CHILECOMPRA,
    SOURCE_CORFO_CENTERS,
    SOURCE_INN_LABS,
    now_iso,
)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", re.I)


def pick_contact_field_for_upsert(incoming: str | None, existing: str | None) -> str | None:
    """Prefer non-empty incoming (source file); otherwise keep existing (manual / hunt import).

    Used by normalize_leads upsert so re-normalize does not wipe enriched contacts.
    """
    inc = (incoming or "").strip()
    if inc:
        return incoming.strip()
    ex = (existing or "").strip()
    return existing if ex else None


def _domain_from_website(url: str | None) -> str | None:
    if not url or not url.strip():
        return None
    url = url.strip().lower()
    if "://" in url:
        url = url.split("://", 1)[1]
    url = url.split("/")[0]
    if url.startswith("www."):
        url = url[4:]
    if not url or "." not in url:
        return None
    # Marketplace/platform domains are not the buyer's domain.
    if url.endswith("mercadopublico.cl") or url.endswith("chilecompra.cl"):
        return None
    return url


def _normalize_org_type_from_name(org_name: str | None) -> str:
    """Infer organization_type_guess from org name when domain is missing."""
    if not org_name:
        return "business"
    n = org_name.lower()
    if "universidad" in n or "uchile" in n or "puc" in n or "utalca" in n or "udec" in n or "usach" in n or "uach" in n:
        return "education"
    if "gob" in n or "ministerio" in n or "servicio" in n or "municipalidad" in n or ".gob." in n:
        return "government"
    return "business"


def normalize_chilecompra(raw: dict[str, Any]) -> dict[str, Any]:
    """Build normalized lead row from ChileCompra raw. Keys match lead_master columns."""
    def get_first(*keys: str) -> str:
        for k in keys:
            v = raw.get(k)
            if v is None:
                continue
            s = str(v).strip()
            if s:
                return s
        return ""

    # Mercado Público bulk CSV: Codigo (line/row id), CodigoExterno (tender id), NombreOrganismo (buyer).
    record_id = get_first(
        "Codigo",
        "Correlativo",
        "id",
        "codigo",
        "tender_id",
        "CodigoExterno",
        "0",
        "Número de Adquisición",
    )
    title = get_first(
        "Nombre",
        "titulo",
        "title",
        "nombre",
        "Nombre de Adquisición",
        "1",
        "Nombre de Adquisición ",
    )
    description = get_first(
        "Descripcion",
        "Descripcion linea Adquisicion",
        "descripcion",
        "description",
        "Descripción de Adquisición",
        "5",
        "DescLineaProductoServicio",
    )
    # Never use numeric column indices like "2" here — in some exports that is Estado / currency, not buyer.
    buyer = get_first(
        "NombreOrganismo",
        "NombreUnidad",
        "comprador",
        "buyer",
        "organismo",
        "org_name",
        "Institución",
        "Organizacion",
        "Unidad de Compra",
        "15",
    )
    # URL fields vary across exports:
    # - some use Link with full fichaLicitacion URL
    # - some use url/link/source_url
    url = get_first("Link", "link", "url", "source_url", "Url")
    if url and not url.startswith("http"):
        url = "https://www.mercadopublico.cl/" + url.lstrip("/")
    # Prefer buyer identity; fall back to title only if we truly have nothing.
    org_name = buyer or (title[:120] if title else "ChileCompra (sin comprador)")

    # Buyer-kind heuristics for explanation and fit (not too granular).
    buyer_lower = org_name.lower()
    if "hospital" in buyer_lower or "servicio de salud" in buyer_lower:
        buyer_kind = "hospital"
    elif "universidad" in buyer_lower or "instituto" in buyer_lower or "docencia" in buyer_lower:
        buyer_kind = "universidad"
    elif buyer_lower.startswith("sag") or "servicio agricola" in buyer_lower:
        buyer_kind = "agricola"
    elif "municipal" in buyer_lower or "ilustre municipalidad" in buyer_lower:
        buyer_kind = "municipal"
    elif "ministerio" in buyer_lower or "gobierno" in buyer_lower:
        buyer_kind = "gobierno"
    else:
        buyer_kind = "publico"

    text = f"{title}\n{buyer}\n{description}"
    tags = equipment_tags_for_leads(text)
    lab_score, lab_tags = lab_context_signals(text)

    # Domain: do NOT take marketplace URL domain; prefer contact email domain or explicit website field.
    domain = _domain_from_website(get_first("sitio", "website")) or (
        domain_of(get_first("contacto_email", "email")) if get_first("contacto_email", "email") else None
    )

    # organization_type_guess: use domain when available, else infer from buyer kind.
    if domain:
        org_type = guess_org_type_from_domain(domain)
    else:
        org_type = "education" if buyer_kind == "universidad" else ("government" if buyer_kind in ("gobierno", "municipal", "agricola") else _normalize_org_type_from_name(org_name))
    now = now_iso()

    # Evidence summary: include buyer + title; keep it readable.
    evid = title.strip()
    if not evid:
        evid = description.strip()
    evid = evid[:420]
    if record_id:
        evid = f"{record_id} — {evid}" if evid else record_id
    return {
        "source_name": SOURCE_CHILECOMPRA,
        "source_type": "procurement",
        "source_record_id": record_id or str(hash((title + buyer + description).strip()))[:16],
        "source_url": url or None,
        "org_name": org_name or None,
        "contact_name": (raw.get("contacto") or raw.get("contact_name")) or None,
        "email": (raw.get("contacto_email") or raw.get("email")) or None,
        "phone": (raw.get("telefono") or raw.get("phone")) or None,
        "website": (raw.get("sitio") or raw.get("website")) or None,
        "domain": domain,
        "region": get_first("RegionUnidad", "region", "region_id", "Region") or None,
        "city": get_first("ComunaUnidad", "ciudad", "city") or None,
        "lead_type": "tender_buyer",
        "organization_type_guess": org_type,
        "buyer_kind": buyer_kind,
        "equipment_match_tags": ",".join(tags) if tags else None,
        "lab_context_score": lab_score,
        "lab_context_tags": ",".join(lab_tags) if lab_tags else None,
        "evidence_summary": evid or None,
        "first_seen_at": now,
        "last_seen_at": now,
        "status": "nuevo",
    }


def normalize_inn_labs(raw: dict[str, Any]) -> dict[str, Any]:
    """Build normalized lead row from INN labs raw."""
    record_id = str(raw.get("id") or raw.get("codigo") or raw.get("nombre") or "")
    if not record_id:
        record_id = str(hash(json.dumps(raw, sort_keys=True)))[:16]
    org_name = str(raw.get("nombre") or raw.get("lab_name") or raw.get("organizacion") or raw.get("laboratorio") or "")
    area = raw.get("area") or raw.get("esquema") or raw.get("acreditacion") or raw.get("accreditation_area") or ""
    text = f"{org_name} {area} {raw.get('descripcion', '')}"
    tags = equipment_tags_for_leads(text)
    website = raw.get("sitio") or raw.get("website") or raw.get("url") or ""
    domain = _domain_from_website(website) or domain_of(raw.get("email") or raw.get("contacto_email"))
    org_type = guess_org_type_from_domain(domain) if domain else _normalize_org_type_from_name(org_name)
    now = now_iso()
    evidence = f"INN acreditado: {area}" if area else "Laboratorio acreditado INN"
    return {
        "source_name": SOURCE_INN_LABS,
        "source_type": "accredited_lab",
        "source_record_id": record_id,
        "source_url": (raw.get("url") or raw.get("link") or website) or None,
        "org_name": org_name or None,
        "contact_name": (raw.get("contacto") or raw.get("contact_name")) or None,
        "email": (raw.get("email") or raw.get("contacto_email")) or None,
        "phone": (raw.get("telefono") or raw.get("phone")) or None,
        "website": website or None,
        "domain": domain,
        "region": (raw.get("region") or raw.get("region_id")) or None,
        "city": (raw.get("ciudad") or raw.get("city")) or None,
        "lead_type": "accredited_lab",
        "organization_type_guess": org_type,
        "equipment_match_tags": ",".join(tags) if tags else None,
        "evidence_summary": evidence[:500] if evidence else None,
        "first_seen_at": now,
        "last_seen_at": now,
        "status": "nuevo",
    }


def normalize_corfo_centers(raw: dict[str, Any]) -> dict[str, Any]:
    """Build normalized lead row from CORFO centers raw."""
    record_id = str(raw.get("id") or raw.get("codigo") or raw.get("nombre") or raw.get("centro") or "")
    if not record_id:
        record_id = str(hash(json.dumps(raw, sort_keys=True)))[:16]
    center = raw.get("centro") or raw.get("nombre_centro") or raw.get("name") or ""
    org_name = str(raw.get("organizacion") or raw.get("org_name") or raw.get("institucion") or center or "")
    if not org_name and center:
        org_name = center
    text = f"{org_name} {center} {raw.get('area', '')} {raw.get('lineas', '')} {raw.get('descripcion', '')}"
    tags = equipment_tags_for_leads(text)
    website = raw.get("sitio") or raw.get("website") or raw.get("url") or ""
    domain = _domain_from_website(website) or domain_of(raw.get("email") or raw.get("contacto_email"))
    org_type = guess_org_type_from_domain(domain) if domain else _normalize_org_type_from_name(org_name)
    now = now_iso()
    evidence = f"Centro I+D: {center}" if center else "Centro CORFO"
    return {
        "source_name": SOURCE_CORFO_CENTERS,
        "source_type": "research_center",
        "source_record_id": record_id,
        "source_url": (raw.get("url") or raw.get("link") or website) or None,
        "org_name": org_name or None,
        "contact_name": (raw.get("contacto") or raw.get("contact_name") or raw.get("director")) or None,
        "email": (raw.get("email") or raw.get("contacto_email") or raw.get("correo")) or None,
        "phone": (raw.get("telefono") or raw.get("phone") or raw.get("fono")) or None,
        "website": website or None,
        "domain": domain,
        "region": (raw.get("region") or raw.get("region_id")) or None,
        "city": (raw.get("ciudad") or raw.get("city")) or None,
        "lead_type": "corfo_center",
        "organization_type_guess": org_type,
        "equipment_match_tags": ",".join(tags) if tags else None,
        "evidence_summary": evidence[:500] if evidence else None,
        "first_seen_at": now,
        "last_seen_at": now,
        "status": "nuevo",
    }


def raw_to_normalized(source_name: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Dispatch to source-specific normalizer. Returns dict of lead_master-like fields."""
    if source_name == SOURCE_CHILECOMPRA:
        return normalize_chilecompra(raw)
    if source_name == SOURCE_INN_LABS:
        return normalize_inn_labs(raw)
    if source_name == SOURCE_CORFO_CENTERS:
        return normalize_corfo_centers(raw)
    raise ValueError(f"Unknown source_name: {source_name}")
