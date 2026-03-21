# AI / ML — implemented summary & how to talk about it

## Three layers (label outputs like this for clients / ChatGPT)

| Layer | Meaning | Examples in this repo |
|-------|---------|----------------------|
| **Exact** | Counts tied to well-defined rows or dates | Total messages, rows with body, **by-year histogram** (GROUP BY `date_iso` year) |
| **Heuristic** | Rule-based signal, not ground truth | Keyword hits (`cotiz`, `proveedor`, NDR-like), domain tables, cotización∧equipo crosses |
| **Exploratory ML** | Sample-only, not operational truth | Embeddings + clusters (MiniLM + K-Means / Agglomerative / optional HDBSCAN) |

**Rule of thumb:** never sell clusters or keyword % as “exact business facts.” SQL year totals ≈ exact for that archive; “15% cotización” = heuristic mention rate; clusters = themes on a **sample**.

---

## What the pipeline does (non-AI)

- **PST → mbox → SQLite → JSONL** (no ML).
- **Deterministic + heuristic report** on full archive: SQL `LIKE`, domains (incl. operational / external), crosses, years.
- **No LLM** in the default import/report path.

---

## What is implemented (AI / ML)

1. **Embeddings:** `all-MiniLM-L6-v2` → `explore_email_clusters.py`, `generate_client_report.py`, `email_ml_explore.py`.
2. **Clustering:** Agglomerative, K-Means; optional HDBSCAN (`pip install hdbscan`).
3. **LLM prompt (optional):** `EMAIL_BUSINESS_SIGNAL_PROMPT.md` — for slices / API, not core dependency.
4. **Equipment models (heuristic):** regex catalog in `email_ml_explore.py`.

---

## What is *not* implemented

Supervised classifier (needs labels), full LLM batch, RAG, NER — see table in previous README sections.

---

## Findings you can paste into ChatGPT (example)

- ~130k messages; ~117k with body; ~18k NDR-heuristic.
- ~15.5% cotización mentions; ~12.8% university tokens; ~3.8% pedido/OC.
- Full corpus = **SQL + heuristics**; clusters = **samples** only.
- Report = mentions & network, not ERP sales.

---

## Next 3 steps (prioritized — consensus / review)

1. **Stratified clustering** — sample by cotización-only, no-bounce, university, or year so clusters aren’t drowned by NDR/newsletters.  
   → `explore_email_clusters.py --sample-mode cotiz|no_bounce|universidad` (+ optional `--year 2016`).
2. **LLM on slices** — high-value filter → chunks + `EMAIL_BUSINESS_SIGNAL_PROMPT.md` (not whole archive).
3. **Small supervised model** — after **200–500 labels** (quote vs noise, etc.), linear or boosting on **same embeddings**.

**Do not rush:** full RAG, BERTopic, fancy NER — unless product clearly needs them.

---

## External review (why this architecture is sound)

* **Separated** deterministic reporting from exploratory ML — avoids slow, expensive, fragile “AI everywhere.”
* **ML where it fits** — discovery / themes on samples; not replacing exact counts.
* **Honest “not implemented”** — builds trust with clients.
* **Regex / model catalog** — often *more* business-useful than abstract topics for lab equipment.

**Verdict:** keep the layered stack; don’t collapse into a single “AI pipeline.”

---

## Commands

```bash
# Clusters on business-like rows only (heuristic slice)
uv run python scripts/ml/explore_email_clusters.py --limit 2000 --sample-mode cotiz --n-clusters 12

# No bounces in sample (cleaner themes)
uv run python scripts/ml/explore_email_clusters.py --limit 2000 --sample-mode no_bounce

uv run python scripts/ml/email_ml_explore.py --limit 5000 --out reports/out/ml.json
```

*Paths:* `generate_client_report.py`, `explore_email_clusters.py`, `email_ml_explore.py`, `EMAIL_BUSINESS_SIGNAL_PROMPT.md`, `ML_EMAIL_OPTIONS.md`, `REPORT_SCOPE_CLIENT.md`.
