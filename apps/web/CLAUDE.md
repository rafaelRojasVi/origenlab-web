# Claude Code — OrigenLab

**Read [`AGENTS.md`](./AGENTS.md) first** for repo-wide rules, business truth, and when to open `docs/`.

## Router (use before coding)

| Need | Open |
|------|------|
| Business facts, copy, categories, contact | `src/data/*` (`company`, `contact`, `categories`, `services`, `brands`, `faq`, `documents`) |
| Deploy, `dist/`, HostGator | `docs/deployment.md` |
| Security / prior claims decisions | `docs/security-audit-v1.md` |
| Reusable workflows | `.claude/skills/*/SKILL.md` |
| Collaborator / AI onboarding | `CONTRIBUTING.md` |
| Company scope & quotation prompt | `docs/company-scope.md` |

Stack: Astro + Tailwind, static site, Spanish-first. Build: `npm run build` → `dist/`.

Do not invent brands, certifications, specs, lead times, or warranty details not in data or docs.
