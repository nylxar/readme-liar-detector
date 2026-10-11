# Golden target (planted lies for before/after evidence)
# Run ONLY in WSL/EC2 sandbox, never on host. Needs node on sandbox PATH
# (see LIAR_EXTRA_PATH). Copy to WSL ~/neathack/golden-work before fixing
# so the original stays broken for the before/after pair.

## Quickstart (lies inside)

```bash
npm run seed
```

```bash
python app.py --port 3000
```

Env: set `DATABASE_URL_WRONG` then run.

App listens on http://localhost:9999 (wrong, real is 3000).

More: https://example.invalid/dead-link-check
