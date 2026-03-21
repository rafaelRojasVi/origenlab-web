# Documentation index

Narrative docs for the email archive pipeline, business mart, external leads, reporting, ML/AI, and validation phases. **Not every file is equally “true” or current** — use the tiers below.

---

## How to read this repo

| If you need… | Read |
|--------------|------|
| Install, commands, layout, GitHub / `.gitignore` | [README.md](../README.md) (repo root) |
| Email → SQLite → mart (design audit) | [PIPELINE_AUDIT.md](PIPELINE_AUDIT.md) |
| Whole-project + leads reporting picture | [PROJECT_AUDIT_AND_REPORTING_PLAN.md](PROJECT_AUDIT_AND_REPORTING_PLAN.md) |
| External Chile leads (implemented) | [LEAD_PIPELINE.md](LEAD_PIPELINE.md) + [CHILE_LEAD_SOURCES.md](CHILE_LEAD_SOURCES.md) (Part I = sources; Part II = repo implementation fit) |
| Client deliverable (`active/`, client pack) | [REPORTS_AND_CLIENT_PACK.md](REPORTS_AND_CLIENT_PACK.md) |
| DR50 ready-8 + top-20 reporting | [READY8_AND_TOP20_REPORTING_PLAN.md](READY8_AND_TOP20_REPORTING_PLAN.md) (regenerate: `scripts/leads/apply_ready8_contact_patch.py`) |
| Deep Research cohorts (legacy vs current) | [DEEP_RESEARCH_RECONCILIATION.md](DEEP_RESEARCH_RECONCILIATION.md) (regenerate: `scripts/leads/reconcile_deepresearch_50_with_current_cohort.py`) |
| Script catalog | [scripts/README.md](../scripts/README.md) |
| Where reports land | [reports/README.md](../reports/README.md), [reports/out/README.md](../reports/out/README.md) |

---

## Tier A — Canonical reference (maintain intentionally)

- [BUSINESS_FILTERING.md](BUSINESS_FILTERING.md) — business vs non-business signal.
- [RUN_BUSINESS_FILTER.md](RUN_BUSINESS_FILTER.md) — how to run filtering.
- [BUSINESS_MART.md](BUSINESS_MART.md) — mart schema and design.
- [LEAD_PIPELINE.md](LEAD_PIPELINE.md) — **implemented** leads pipeline (replaces “plan” for operations).
- [CHILE_LEAD_SOURCES.md](CHILE_LEAD_SOURCES.md) — sources, keyword packs, and **Part II** implementation analysis vs this repo. ([CHILE_LEAD_SOURCES_IMPLEMENTATION_ANALYSIS.md](CHILE_LEAD_SOURCES_IMPLEMENTATION_ANALYSIS.md) redirects here.)
- [REPORTS_AND_CLIENT_PACK.md](REPORTS_AND_CLIENT_PACK.md) — `active/` vs `client_pack_latest/`.
- [RUN_AFTER_IMPORT.md](RUN_AFTER_IMPORT.md), [RUN_ALL.md](RUN_ALL.md) — post-import / batch run entrypoints (verify paths against `scripts/` if something fails).

---

## Tier B — Auto-generated or regenerate-only (do not edit by hand)

| Artifact | Produced by |
|----------|-------------|
| [CONTACT_READINESS_AUDIT.md](CONTACT_READINESS_AUDIT.md) | `uv run python scripts/leads/audit_contact_readiness.py` |
| `reports/out/active/leads_ready_to_contact.csv` (and related) | same |
| [READY8_AND_TOP20_REPORTING_PLAN.md](READY8_AND_TOP20_REPORTING_PLAN.md) | `uv run python scripts/leads/apply_ready8_contact_patch.py` |
| [DEEP_RESEARCH_RECONCILIATION.md](DEEP_RESEARCH_RECONCILIATION.md) | `uv run python scripts/leads/reconcile_deepresearch_50_with_current_cohort.py` |

Counts inside the contact-readiness audit **reflect your local** `leads_contact_hunt_current.csv` + SQLite at run time.

---

## Tier C — Audits, scope, and output maps (occasionally stale)

- [PIPELINE_AUDIT.md](PIPELINE_AUDIT.md) — PST/mbox/SQLite flow (dated snapshot; verify scripts in repo if paths change).
- [PROJECT_AUDIT_AND_REPORTING_PLAN.md](PROJECT_AUDIT_AND_REPORTING_PLAN.md) — broad architecture + reporting plan (large; overlaps partially with PIPELINE + LEAD_PIPELINE).
- [OUTPUTS_OVERVIEW.md](OUTPUTS_OVERVIEW.md) — email/ML report outputs; references `scripts/reports/run_all.sh` and related scripts.
- [CLIENT_REPORT.md](CLIENT_REPORT.md), [REPORT_SCOPE_CLIENT.md](REPORT_SCOPE_CLIENT.md) — client HTML/JSON report shape and scope.
- [LEAD_ACCOUNT_LAYER.md](LEAD_ACCOUNT_LAYER.md) — account-layer concepts.

---

## Tier D — Phase 2 validation / extraction (many small files)

Detailed phase notes:

- [PHASE2_BODY_EXTRACTION.md](PHASE2_BODY_EXTRACTION.md)
- [PHASE2_1_VALIDATION.md](PHASE2_1_VALIDATION.md), [PHASE2_2_VALIDATION.md](PHASE2_2_VALIDATION.md)
- [PHASE2_QUOTES_SIGNATURES.md](PHASE2_QUOTES_SIGNATURES.md)
- [PHASE2_3_ATTACHMENTS.md](PHASE2_3_ATTACHMENTS.md)
- [PHASE2_4_PLAN.md](PHASE2_4_PLAN.md), [PHASE2_4_ATTACHMENT_EXTRACTION.md](PHASE2_4_ATTACHMENT_EXTRACTION.md)

**Consolidation idea (optional):** merge into a single `PHASE2_EMAIL_EXTRACTION.md` with subheadings to reduce file count — no urgency if you still navigate by phase name.

---

## Tier E — ML / AI / prompts / roadmap

- [AI_ML_IMPLEMENTED_SUMMARY.md](AI_ML_IMPLEMENTED_SUMMARY.md) — **codebase** ML features (preferred over machine snapshots).
- [AI_READINESS_AUDIT.md](AI_READINESS_AUDIT.md) — **one-machine** GPU/Python snapshot; labeled as such in-file.
- [ML_EMAIL_OPTIONS.md](ML_EMAIL_OPTIONS.md), [DERIVED_INSIGHTS_OPTIONS.md](DERIVED_INSIGHTS_OPTIONS.md)
- [EMAIL_BUSINESS_SIGNAL_PROMPT.md](EMAIL_BUSINESS_SIGNAL_PROMPT.md), [CHATGPT_PROMPT_FINDINGS_AND_NEXT.md](CHATGPT_PROMPT_FINDINGS_AND_NEXT.md)
- [EXTENSION_PLAN.md](EXTENSION_PLAN.md)

**Consolidation idea (optional):** move prompts into `docs/prompts/` or an appendix inside [EXTENSION_PLAN.md](EXTENSION_PLAN.md).

---

## Tier F — Historical or narrative only

- [LEAD_PIPELINE_PLAN.md](LEAD_PIPELINE_PLAN.md) — **pre-implementation plan**; superseded by [LEAD_PIPELINE.md](LEAD_PIPELINE.md) (banner at top).
- [deep-research-report.md](deep-research-report.md) — narrative from a DR session; not the operational reconciliation (see [DEEP_RESEARCH_RECONCILIATION.md](DEEP_RESEARCH_RECONCILIATION.md)).

---

## Repo policies (not technical pipeline docs)

- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md), [SECURITY.md](../SECURITY.md) — community and security policy; keep as-is unless governance changes.

---

## Are “all docs true”?

- **Yes** as *descriptions of intent or a dated snapshot* when authored.
- **No** as *automatically current* — scripts, paths, and counts drift. Prefer Tier A + regenerate Tier B after operational changes.
- **Contradictions to watch:** `reports/README.md` (default reports outside repo) vs `reports/out/README.md` (repo-local `full_*` runs) — both can be valid depending on `ORIGENLAB_REPORTS_DIR` and which script you run.
