## Summary

<!-- What changed and why -->

## Scope

- [ ] `apps/web` (Astro site)
- [ ] `apps/email-pipeline` (Python / uv)
- [ ] Root / shared (CI, docs, tooling)

## Checklist

### Web (`apps/web`)

- [ ] `npm run check` passes (if you changed site code)
- [ ] `npm run build` passes (if you changed site code)
- [ ] Business/contact data lives in `apps/web/src/data/*` (not hardcoded in pages)

### Email pipeline (`apps/email-pipeline`)

- [ ] `uv run pytest` passes (if you changed pipeline code)
- [ ] No secrets, PST/mbox/SQLite, or sensitive CSVs committed (see app `.gitignore`)

## Notes / screenshots

<!-- Optional -->
