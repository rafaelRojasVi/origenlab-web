# What else can be derived from the email reports?

Based on the current reports (business filter summaries, category counts, sender domains, unique_emails, scope/summary with aggregates), these are **additional relationships and outputs** that are feasible with the same data (subject, body, sender, recipients, date).

---

## Already in the reports

- **Volume & time:** total messages, by year, by year for “cotización”
- **Classification:** primary_category + tags (internal, institution, business_core, logistics, etc.), category counts
- **Sender side:** top sender domains by view (all / operational_no_ndr / business_only / business_only_external), top raw senders
- **Signals in text:** aggregates for cotización, universidad, factura, pedido/OC, bounce-like, and **equipment** (eq_balanza, eq_centrifuga, etc.)
- **Cotización ∧ equipment:** cotiz_balanza, cotiz_microscopio, etc. (already in `generate_client_report` SQL)
- **Unique emails:** who appears as sender and/or in recipients, with counts

---

## 1. Equipment ↔ University / institution

**Idea:** Which equipment types are most mentioned in traffic with universities (or institution-tagged senders)?

**Output examples:**
- Table: `domain` (or “institution”), `eq_balanza`, `eq_centrifuga`, … (message counts per domain × equipment)
- Or: “Universities” rollup → top equipment mentioned in those threads (e.g. balanza, microscopio, centrífuga)

**What you need:**
- For each message: sender domain (already derivable) + which of the eq_* and “universidad”/institution signals appear in body/subject (same LIKE logic as in `_merged_aggregate_sql()`).
- One pass: stream `(id, sender, body, subject)` (or run SQL with a domain expression if you add it), then in Python group by sender domain (or by “is_institution” / “is_university_domain”) and count per (domain_or_type, equipment_flag).
- Optional: restrict to `primary_category = 'institution'` or to domains you tag as university (e.g. uach.cl, udec.cl, med.puc.cl, etc.) so the report is “equipment × university relations”.

**Use:** “Which universities talk to us about which equipment?” / “What do we quote most to the education sector?”

---

## 2. Equipment ↔ sender domain (any domain)

**Idea:** Per sender domain, how many messages mention each equipment type (or cotización ∧ equipment).

**Output:**
- Table: `sender_domain`, `eq_balanza`, `eq_centrifuga`, … (and optionally `cotiz_balanza`, etc.)
- Filter to top N domains by volume to keep the table readable.

**What you need:**
- Same as above: one streaming pass with (sender, body, subject), compute domain + equipment flags, then `GROUP BY domain` and SUM each flag.
- No new schema; reuses the same LIKE rules as the global aggregates.

**Use:** “Which clients/suppliers (by domain) are in threads about balanzas, HPLC, etc.?” Complements “equipment × university” by covering all domains.

---

## 3. University / institution relations (summary)

**Idea:** A dedicated “university relations” view: list of domains that count as university/institution, with message count and optionally “top equipment mentioned” in those threads.

**Output:**
- List of domains (e.g. uach.cl, udec.cl, med.puc.cl, uc.cl, unab.cl, usm.cl, usach.cl, santotomas.cl, etc.) with:
  - `message_count`
  - optional: `top_equipment` (e.g. eq_balanza, eq_centrifuga) or counts per equipment
- Optionally same for “institution” in general (including hospitals, research centers) if you tag them.

**What you need:**
- A small “university/institution domain” list (from current top sender lists you already have), or a rule (e.g. `.cl` with known substrings, or `primary_category = 'institution'`).
- One pass: filter to those domains (or to messages with institution tag), then aggregate by domain and by equipment flags.

**Use:** “Who are our main university/institution contacts and what equipment appears in those conversations?”

---

## 4. Domain type / sector (and then equipment by sector)

**Idea:** Classify each sender domain into broad types (e.g. university, government, supplier, logistics, marketplace, other), then show volume and equipment mix per type.

**Output:**
- Table: `sector` (e.g. university, government, supplier, logistics, marketplace), `message_count`, and optionally counts per equipment or “top equipment” per sector.
- Or: `domain`, `sector`, `message_count`, then a second table sector × equipment.

**What you need:**
- A mapping domain → sector (manual list or rules: e.g. `gob.cl`, `mercadopublico.cl` → government; `ohaus.com`, `hielscher.com` → supplier; `dhl.com` → logistics; known .edu / uach, udec, … → university).
- Same streaming pass: for each message, sender_domain → sector, then aggregate (sector, equipment) or (sector, domain, equipment).

**Use:** “How much traffic and what equipment themes by segment (universities vs suppliers vs government)?”

---

## 5. Recipient / contrapartes (who we send to)

**Idea:** Top domains (or addresses) that appear in **To/Cc** (recipients), excluding the company’s own domain, to see “who we send to” (contrapartes).

**What you have:** `unique_emails.csv` has `count_in_recipients`; so you have recipient-side presence. What’s missing is aggregation **by domain** for recipients only (and possibly by view, e.g. business_only).

**Output:**
- `top_recipient_domains` (and optionally `top_recipient_domains_external` excluding labdelivery.cl), with message counts.
- Optional: same by view (e.g. business_only) if you filter by message tags.

**What you need:**
- Parse `recipients` per message, extract domains, exclude internal domain, then count. Either in the same domain-streaming pass (if you already have recipients) or a dedicated pass over (sender, recipients, tags).
- If the report already has “top_recipient_domains” in summary, this is just making sure it’s populated and optionally split by view.

**Use:** “Which external domains do we send the most to?” Complements sender-side rankings.

---

## 6. Equipment by year

**Idea:** Time trend of equipment mentions (and optionally cotización ∧ equipment by year).

**Output:**
- `by_year_eq_balanza`, `by_year_eq_centrifuga`, … (message counts per year per equipment), or a matrix year × equipment.
- Optional: same for cotiz_balanza, cotiz_centrifuga, etc. by year.

**What you need:**
- Same LIKE logic for equipment (and cotiz) in a query that groups by `strftime('%Y', date_iso)` (and filters to messages with date). One extra scan or extension of the existing year scan.

**Use:** “Which equipment lines grew or shrank in the archive over time?”

---

## 7. Supplier / brand ↔ equipment (by domain)

**Idea:** Map known supplier domains (Ohaus, Hielscher, IKA, etc.) to “equipment families” and show how often they appear in threads that mention each equipment type.

**Output:**
- Table: supplier_domain (or brand), equipment_type, message_count.
- Or: “In threads mentioning balanza, which sender domains (suppliers) appear most?” (already partly visible in sender_domain rankings; this makes the link to equipment explicit.)

**What you need:**
- Small mapping: domain → brand/equipment_family (e.g. ohaus.com → balanza; hielscher.com → ultrasonics; ika.net.br → lab equipment).
- One pass: for each message, sender_domain + equipment flags; then aggregate (supplier_domain, equipment_type) or (equipment_type, sender_domain).

**Use:** “Which suppliers appear in conversations about which equipment?” (e.g. Ohaus ↔ balanza.)

---

## 8. Equipment co-occurrence (which equipment appear together)

**Idea:** Count messages that mention two (or more) equipment types, to see “lab setup” clusters (e.g. balanza + pipetas, centrífuga + incubadora).

**Output:**
- Pairs (eq_A, eq_B) with message count; or a heatmap equipment × equipment.

**What you need:**
- One pass: for each message, compute the set of eq_* flags that appear (from body/subject); for each pair in the set, increment a counter. No new schema.

**Use:** “Which equipment are often mentioned together?” (e.g. for bundles or segment reporting.)

---

## 9. Model / brand mentions (regex) by domain or sector

**Idea:** You already have regex-based model extraction in `email_ml_explore.py` (Ohaus Adventurer, IKA RCT, etc.). Extend to “per domain” or “per sector” (e.g. which models appear in university vs supplier traffic).

**Output:**
- Table: domain (or sector), model_family, span, count.
- Or: top models mentioned in institution vs business_core messages.

**What you need:**
- Run the same regex over (subject, body) in a pass where you also have sender_domain (and optionally sector or category); aggregate by (domain or sector, model).

**Use:** “Which exact models are mentioned in university vs supplier emails?” (complements “equipment × university”.)

---

## Summary table

| Derived output              | Main use                               | Effort (data you have)     |
|----------------------------|----------------------------------------|----------------------------|
| Equipment × university     | Which equipment per uni / institution  | 1 pass + domain + LIKE     |
| Equipment × domain          | Which equipment per sender domain      | 1 pass + domain + LIKE     |
| University relations       | List unis + volume + top equipment     | Domain list + same pass    |
| Domain type / sector       | Segment (uni, gov, supplier, etc.)    | Domain→sector map + pass   |
| Recipient / contrapartes   | Who we send to (by domain)             | Parse recipients + count   |
| Equipment by year          | Time trend per equipment               | Group by year + LIKE       |
| Supplier ↔ equipment       | Which suppliers per equipment type     | Domain→brand map + pass    |
| Equipment co-occurrence    | Pairs of equipment in same message     | Per-message eq set + pairs |
| Model mentions by domain   | Which models per domain/sector         | Regex + domain/sector     |

All of these use the same underlying data (subject, body, sender, recipients, date); no new ingestion. Implementation is mostly one or two streaming passes and optional lookup tables (domain → sector, domain → university, domain → supplier/brand).

---

## Suggested order

1. **Equipment × domain** and **Equipment × university** — direct answers to “equipment vs university relations” and “which domains talk about which equipment”.
2. **University relations** — small summary table (domains + volume + top equipment) for client-facing “who are our main university contacts”.
3. **Recipient / contrapartes** — if you want “who we send to” next to “who sends to us”.
4. **Domain type / sector** — then equipment by sector, for higher-level reporting.
5. **Equipment by year** — if time trends are important.
6. **Supplier ↔ equipment** and **Equipment co-occurrence** — for deeper product/segment analysis.

If you tell me which of these you want first (e.g. “equipment × university” + “university relations table”), I can outline the exact query/script steps or add them to the report script.
