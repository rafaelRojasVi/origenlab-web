## Contributing

Thanks for contributing.

### Development setup

- **Python**: 3.12
- **Env/deps**: `uv`

```bash
uv python install 3.12
uv sync --group dev
```

### Running checks

```bash
uv run pytest
```

### Data safety

- **Do not** commit PSTs, mbox files, SQLite DBs, JSONL exports, or client report outputs.
- Keep real data **outside the repo** (see `README.md` and `.env.example`).

