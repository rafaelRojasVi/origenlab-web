# Phase 2.2 — Quotes and signatures

**Goal:** Provide two additional body variants for analytics and search:

- `full_body_clean` — fuller cleaned body text (good for audit/search/reference).
- `top_reply_clean` — best-effort newest meaningful reply text, with quoted chains and signatures reduced where safe.

These are derived from existing Phase 2.1 fields and do **not** overwrite any previous columns.

---

## 1. Field semantics

### Source fields (Phase 2.1)

- `body_text_raw` — primary extracted text (plain preferred, fallback HTML→text).
- `body_text_clean` — improved cleaned text (normalized, better HTML cleaning).
- `body_source_type` — `plain` | `html` | `mixed` | `empty`.

### New fields (Phase 2.2)

- `full_body_clean` (TEXT)
  - Computed by `normalize_full_body(structured)`.
  - Precedence:
    1. If `body_text_clean` is non-empty → normalize and use that.
    2. Else if `body_text_raw` is non-empty → normalize and use that.
    3. Else → `""`.
  - Intended as the “best available full text” per message.

- `top_reply_clean` (TEXT)
  - Computed by `extract_top_reply(full_body_clean)`.
  - Should contain the **newest reply text**:
    - attempts to cut off quoted reply chains,
    - then attempts to remove a trailing signature block.
  - **Conservative fallback:** if no clear quote/signature boundary is detected, or if stripping would remove everything, `top_reply_clean` falls back to `full_body_clean`.

---

## 2. Heuristics

### 2.1 Reply header and quote detection

Implementation lives in:

- `parse_mbox.py`:
  - `_cut_at_reply_headers(text: str) -> str`
  - `extract_top_reply(full_body_clean: str) -> str`

Patterns considered (case-insensitive):

- English / general:
  - `On ... wrote:`
  - `From:`
  - `Sent:`
  - `-----Original Message-----`
- Spanish:
  - `El ... escribió:`
  - `De:`
  - `Enviado el:`
- Quoted blocks:
  - Lines starting with `>` within a block.

Behaviour:

- Split body into lines.
- Scan for:
  - a reply header line matching these patterns, or
  - the beginning of a `>`-quoted block (after at least one non-empty line).
- When found, cut the body **above** that line; everything below is treated as quoted history.
- If nothing matches, return the text unchanged.

### 2.2 Signature handling

Implementation in:

- `parse_mbox.py`:
  - `_strip_signature_block(text: str) -> str`

Signature starters (case-insensitive):

- `--`
- `Saludos`
- `Saludos cordiales`
- `Atentamente`
- `Best regards`
- `Kind regards`
- `Regards`
- `Enviado desde mi`

Behaviour:

- Split into lines, scan from bottom up for a line starting with any of the signature starters.
- Require at least a couple of lines above the signature (to avoid stripping messages that consist only of a short reply + greeting).
- If found, cut at that line (keep everything above, drop signature block).
- If the cut would remove almost everything, or if no candidate is found, return the text unchanged.

### 2.3 Combined pipeline

`extract_top_reply(full_body_clean)`:

1. Start from `full_body_clean`.
2. Apply `_cut_at_reply_headers`.
3. Apply `_strip_signature_block`.
4. If the resulting text is empty, fall back to the original `full_body_clean`.

---

## 3. Usage

### Ingestion path

- `scripts/ingest/02_mbox_to_sqlite.py`:
  - Calls `extract_body_structured(msg)` → `structured` dict.
  - Calls `extract_full_and_top_reply(structured)` → `(full_body_clean, top_reply_clean)`.
  - Passes both into `insert_email(...)` when inserting each row.

### Backfill for existing rows

- Script: `scripts/validation/backfill_phase2_2_text_fields.py`
  - Reads rows where `full_body_clean` is NULL or empty.
  - For each row, builds a mini `structured` dict from `body_text_raw` and `body_text_clean`.
  - Calls `extract_full_and_top_reply` and `UPDATE`s `full_body_clean` and `top_reply_clean`.
  - Runs in batches (10,000 rows) and logs progress.

Example:

```bash
uv run python scripts/validation/backfill_phase2_2_text_fields.py
```

For a full rebuild, you can also re-run the ingestion pipeline, which will populate the fields directly.

---

## 4. Tests

New tests live in `tests/test_quotes_signatures.py` and cover:

- **No quotes / no signatures:**
  - `full_body_clean` and `top_reply_clean` are identical and match the original body.
- **English reply header (`On ... wrote:`):**
  - `top_reply_clean` keeps the newest content and excludes the header + quoted text.
- **Spanish reply header (`El ... escribió:` / `De:` / `Enviado el:`):**
  - Same as above, for Spanish-style replies.
- **Outlook original message separator (`-----Original Message-----`):**
  - `top_reply_clean` drops the original-message section.
- **Signature removal:**
  - Lines like `Saludos cordiales`, `Best regards`, etc., and following name/footer are removed from `top_reply_clean`.
- **Short client reply:**
  - Very short replies such as `Ok, gracias.\n\nSaludos` are **not** over-stripped; `top_reply_clean` falls back to `full_body_clean`.
- **No patterns present:**
  - `top_reply_clean == full_body_clean`.

Run all tests:

```bash
uv run pytest -v
```

---

## 5. Limitations and trade-offs

- Heuristics are intentionally conservative:
  - They avoid aggressive stripping that might remove real business content.
  - When in doubt, `top_reply_clean` == `full_body_clean`.
- Some complex or unusual reply formats may keep more quoted history than ideal.
- Signature detection is based on common phrases; highly customized signatures may be kept.
- The logic is language-biased towards Spanish and English; other languages may not be handled as well yet.

Despite these limitations, `top_reply_clean` is generally:

- Shorter and more focused than `full_body_clean`.
- Better suited for downstream analytics (entity extraction, intent classification, clustering).
- Still backed by `full_body_clean` and all original fields for audit or fallbacks.

