"""Deterministic organization / domain normalization for lead account rollup."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse

from origenlab_email_pipeline.business_mart import domain_of

# Placeholders and junk tokens (lowercase comparison after normalize).
_JUNK_EXACT = frozenset(
    {
        "",
        "-",
        "--",
        "n/a",
        "na",
        "none",
        "null",
        "sin comprador",
        "sin información",
        "sin informacion",
        "no aplica",
        "s/i",
        "si",
        "no",
        "aceptada",
        "rechazada",
        "peso chileno",
    }
)

_JUNK_PREFIXES = (
    "chilecompra sin comprador",  # after punctuation fold
    "chilecompra (sin comprador",
    "sin comprador",
)

# Status-like single tokens (not institution names).
_JUNK_SINGLE_WORDS = frozenset({"si", "no", "aceptada", "rechazada", "pendiente", "n/a", "na"})

_WS_RE = re.compile(r"\s+")
_PUNCT_STRIP_RE = re.compile(r'["""\'´`.,;:!?¿¡()[\]{}|/\\]+')
_LEGAL_SUFFIX_RE = re.compile(
    r"\b(s\.?\s*a\.?|s\.?\s*p\.?\s*a\.?|ltda\.?|e\.?i\.?r\.?l\.?|spa)\.?\s*$",
    re.I,
)


def normalize_org_name(value: str | None) -> str:
    """Lowercase, trim, collapse spaces, strip some punctuation, fold accents (NFKD).

    Conservative: does not aggressively merge distinct institutions.
    """
    if value is None:
        return ""
    s = str(value).strip().lower()
    if not s:
        return ""
    # Normalize unicode (keep compatibility; strip combining marks for matching)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = _PUNCT_STRIP_RE.sub(" ", s)
    s = _LEGAL_SUFFIX_RE.sub("", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def is_junk_org_name(value: str | None) -> bool:
    """True if value is empty, placeholder, or clearly not an institution name."""
    if value is None:
        return True
    raw = str(value).strip()
    if not raw:
        return True
    raw_lower = raw.lower()
    if raw_lower in ("n/a", "na", "n a", "sin información", "sin informacion"):
        return True
    n = normalize_org_name(raw)
    if not n or len(n) < 2:
        return True
    if n in _JUNK_EXACT:
        return True
    for p in _JUNK_PREFIXES:
        if n.startswith(p):
            return True
    parts = n.split()
    if len(parts) == 1 and parts[0] in _JUNK_SINGLE_WORDS:
        return True
    # Very short gibberish
    if len(n) <= 2 and not any(c.isdigit() for c in n):
        return True
    return False


def normalize_domain(url_or_domain: str | None) -> str | None:
    """Return registrable-style hostname lowercase, or None. Reuses email domain parsing."""
    if url_or_domain is None:
        return None
    s = str(url_or_domain).strip()
    if not s:
        return None
    s = s.lower()
    if "://" in s:
        host = urlparse(s).hostname
        if not host:
            return None
        s = host
    if s.startswith("www."):
        s = s[4:]
    if "@" in s:
        # accidental email pasted
        s = s.split("@")[-1]
    s = s.split("/")[0].split(":")[0].strip()
    if not s or "." not in s:
        return None
    if s.endswith("mercadopublico.cl") or s.endswith("chilecompra.cl"):
        return None
    # Validate via existing helper (returns None for invalid)
    d = domain_of(f"x@{s}")
    return d


def account_dedupe_key(normalized_name: str, primary_domain: str | None) -> str:
    """Stable key for clustering lead_master rows into one account."""
    nn = normalize_org_name(normalized_name) or ""
    dom = (primary_domain or "").strip().lower()
    return f"{nn}||{dom}"


def better_canonical_name(current: str, candidate: str) -> str:
    """Prefer longer, more specific display names."""
    c = (candidate or "").strip()
    cur = (current or "").strip()
    if not c:
        return cur
    if not cur:
        return c
    if len(c) > len(cur):
        return c
    return cur
