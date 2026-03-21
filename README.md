# OrigenLab

Monorepo for OrigenLab engineering: **marketing site** (Astro) and **email / lead pipeline** (Python).

| App | Path | Stack |
|-----|------|--------|
| Website | [`apps/web/`](apps/web/) | Astro 5, Tailwind 4, Node 20 (see `apps/web/.nvmrc`) |
| Email pipeline | [`apps/email-pipeline/`](apps/email-pipeline/) | Python 3.12, uv, optional CUDA ML — see that app’s [README](apps/email-pipeline/README.md) |

## Quick start

**Website**

```bash
cd apps/web
npm ci
npm run build
```

**Email pipeline**

```bash
cd apps/email-pipeline
uv sync
uv run pytest
```

## CI

GitHub Actions workflows are path-filtered under [`.github/workflows/`](.github/workflows/): changes under `apps/web/` run the web build; changes under `apps/email-pipeline/` run Python tests.

## New remote

After you create an empty GitHub repository for this monorepo:

```bash
cd /path/to/this/clone
git remote add origin git@github.com:YOUR_USER/YOUR_MONOREPO.git
git push -u origin main
```

## Legacy `origenlab-web` repository

The site history was imported into `apps/web/` with **`git subtree`**. The standalone repo [`origenlab-web`](https://github.com/rafaelRojasVi/origenlab-web) should be **archived** (or given a README redirect) so work continues only here. See [docs/MONOREPO.md](docs/MONOREPO.md).
