"""Lead pipeline schema. Tables are created by the leads pipeline, not by db.init_schema."""

from __future__ import annotations

import sqlite3

LEAD_SCHEMA_SQL = """
-- Raw records from external sources (idempotent re-fetch).
CREATE TABLE IF NOT EXISTS external_leads_raw (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  raw_json TEXT,
  source_url TEXT,
  UNIQUE(source_name, source_record_id)
);
CREATE INDEX IF NOT EXISTS idx_external_leads_raw_source ON external_leads_raw(source_name, source_record_id);
CREATE INDEX IF NOT EXISTS idx_external_leads_raw_fetched ON external_leads_raw(source_name, fetched_at);

-- Normalized leads for prospecting.
CREATE TABLE IF NOT EXISTS lead_master (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT NOT NULL,
  source_type TEXT,
  source_record_id TEXT,
  source_url TEXT,
  org_name TEXT,
  contact_name TEXT,
  email TEXT,
  phone TEXT,
  website TEXT,
  domain TEXT,
  region TEXT,
  city TEXT,
  lead_type TEXT,
  organization_type_guess TEXT,
  buyer_kind TEXT,
  equipment_match_tags TEXT,
  lab_context_score REAL,
  lab_context_tags TEXT,
  evidence_summary TEXT,
  first_seen_at TEXT,
  last_seen_at TEXT,
  priority_score REAL,
  priority_reason TEXT,
  fit_bucket TEXT,
  status TEXT DEFAULT 'nuevo',
  review_owner TEXT,
  last_reviewed_at TEXT,
  next_action TEXT,
  notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_lead_master_source ON lead_master(source_name);
CREATE INDEX IF NOT EXISTS idx_lead_master_domain ON lead_master(domain);
CREATE INDEX IF NOT EXISTS idx_lead_master_status ON lead_master(status);
CREATE INDEX IF NOT EXISTS idx_lead_master_priority ON lead_master(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_lead_master_last_seen ON lead_master(last_seen_at);

-- Matching to existing organization_master (read-only from mart).
CREATE TABLE IF NOT EXISTS lead_matches_existing_orgs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id INTEGER NOT NULL,
  matched_domain TEXT NOT NULL,
  matched_org_name TEXT,
  match_type TEXT NOT NULL,
  confidence_score REAL NOT NULL,
  already_in_archive_flag INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(lead_id) REFERENCES lead_master(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_lead_matches_lead_id ON lead_matches_existing_orgs(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_matches_domain ON lead_matches_existing_orgs(matched_domain);

-- Manual / Deep Research contact-hunt data (v1.2+). Not modified by normalize_leads.
CREATE TABLE IF NOT EXISTS lead_outreach_enrichment (
  lead_id INTEGER PRIMARY KEY,
  enrichment_json TEXT NOT NULL,
  source_file TEXT,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(lead_id) REFERENCES lead_master(id) ON DELETE CASCADE
);
"""


def ensure_leads_tables(conn: sqlite3.Connection) -> None:
    """Create lead tables if they do not exist. Idempotent."""
    conn.executescript(LEAD_SCHEMA_SQL)
    # Additive migrations for v1 refinements (safe on existing DBs).
    for col in (
        "buyer_kind TEXT",
        "lab_context_score REAL",
        "lab_context_tags TEXT",
        "fit_bucket TEXT",
    ):
        try:
            conn.execute(f"ALTER TABLE lead_master ADD COLUMN {col}")
            conn.commit()
        except sqlite3.OperationalError:
            pass
    conn.commit()
