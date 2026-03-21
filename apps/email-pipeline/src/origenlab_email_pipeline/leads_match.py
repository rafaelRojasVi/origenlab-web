"""Match lead_master to organization_master. Read-only from mart; write to lead_matches_existing_orgs."""

from __future__ import annotations

import re
import sqlite3


def _normalize_name_for_match(name: str | None) -> str:
    """Lowercase, strip, remove common suffixes for simple name comparison."""
    if not name or not name.strip():
        return ""
    s = name.lower().strip()
    for suffix in (" s.a.", " sa", " spa", " ltda", " s.a", " spa.", " ltda."):
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def match_leads_to_mart(conn: sqlite3.Connection) -> int:
    """For each lead in lead_master, try to match organization_master by domain then by normalized name.
    Writes to lead_matches_existing_orgs. Does not mutate mart tables.
    Returns number of match rows written.
    """
    # Check if organization_master exists (mart may not be built).
    try:
        conn.execute("SELECT 1 FROM organization_master LIMIT 1")
    except sqlite3.OperationalError:
        conn.rollback()
        return 0

    conn.execute("DELETE FROM lead_matches_existing_orgs")
    count = 0

    # Build domain -> (domain, org_name_guess) from mart.
    domain_to_org: dict[str, tuple[str, str]] = {}
    for row in conn.execute("SELECT domain, organization_name_guess FROM organization_master WHERE domain IS NOT NULL AND domain != ''"):
        d, name = (row[0] or "").strip().lower(), (row[1] or "").strip()
        if d:
            domain_to_org[d] = (d, name)

    # Normalized name -> (domain, org_name) for name fallback (first match wins).
    name_to_org: dict[str, tuple[str, str]] = {}
    for row in conn.execute("SELECT domain, organization_name_guess FROM organization_master WHERE organization_name_guess IS NOT NULL"):
        d, name = (row[0] or "").strip(), (row[1] or "").strip()
        key = _normalize_name_for_match(name)
        if key and key not in name_to_org:
            name_to_org[key] = (d or "", name)

    for row in conn.execute(
        "SELECT id, domain, org_name FROM lead_master"
    ):
        lead_id, lead_domain, lead_org_name = row[0], (row[1] or "").strip().lower(), (row[2] or "").strip()

        # 1) Domain exact match
        if lead_domain and lead_domain in domain_to_org:
            matched_domain, matched_org_name = domain_to_org[lead_domain]
            conn.execute(
                """
                INSERT INTO lead_matches_existing_orgs (lead_id, matched_domain, matched_org_name, match_type, confidence_score, already_in_archive_flag)
                VALUES (?, ?, ?, 'domain', 1.0, 1)
                """,
                (lead_id, matched_domain, matched_org_name),
            )
            count += 1
            continue

        # 2) Name fallback: normalized lead org_name vs mart organization_name_guess
        key = _normalize_name_for_match(lead_org_name)
        if key and key in name_to_org:
            matched_domain, matched_org_name = name_to_org[key]
            conn.execute(
                """
                INSERT INTO lead_matches_existing_orgs (lead_id, matched_domain, matched_org_name, match_type, confidence_score, already_in_archive_flag)
                VALUES (?, ?, ?, 'name_fuzzy', 0.7, 1)
                """,
                (lead_id, matched_domain or "", matched_org_name),
            )
            count += 1

    conn.commit()
    return count
