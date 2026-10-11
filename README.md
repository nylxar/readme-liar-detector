# readme-liar-detector

Agent that proves README claims by running them sandboxed. Parses commands, env keys, ports, and links from a README, executes each command in an isolated env, checks links, asks one LLM for a docs-fix vs code-fix verdict, and outputs a Truth Score 0–100 plus a minimal fix.

Pipeline: `parse (claims.py) → sandbox try (sandbox.py) → link check (links.py) → LLM verdict (run.py) → deterministic fix (fix.py) → re-run → rescore`.

## Repo layout

- `src/agent/claims.py` — extracts commands (fenced bash + inline `npm`/`pip`/`python`/`node`), backticked env keys, ports, links. Caps: 10 commands, 20 env keys, 10 ports/links.
- `src/agent/sandbox.py` — isolated runner: clean env (`PATH`/`HOME`/`CI` only), 60s timeout, `cwd` = repo copy. `LIAR_EXTRA_PATH` may prepend one Linux-only dir under `/home/` or `/tmp/` (e.g. node). Never passes host secrets.
- `src/agent/links.py` — stdlib HEAD→GET reachability check, 10s timeout. No LLM, no secrets sent.
- `src/agent/run.py` — verify loop + one LLM call (`docs-fix` | `code-fix` | `ok` + score/reason).
- `src/agent/fix.py` — deterministic code-fix, no LLM: if `npm run <s>` maps to `node <file>` in `package.json` and `<file>` is missing, scaffolds a minimal stub (path-guarded to workdir), then re-runs and rescores.
- `golden/` — planted-lie fixture (`npm run seed` → missing `scripts/seed.js`, wrong env key/port, dead link). Keep broken; copy before fixing.
- `traces/README.md` — before/after run evidence. `work/` — gitignored fix scratch.

## Requirements

- Python 3.13, `uv`
- WSL/Linux sandbox for runs (never run with secrets on an untrusted host)
- Optional: LiteLLM key (`MODEL=claude-haiku` default, 1 LLM call per repo)

## Quickstart (isolated)

All runs in WSL, keys only in WSL `.env` (`chmod 600`, gitignored). Never commit real keys; `.env.example` holds placeholders.

```bash
cp -r readme-liar-detector ~/neathack/
cd ~/neathack/readme-liar-detector
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -U -r requirements.txt
printf 'LITELLM_API_KEY=...\n' > .env
export LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1 MODEL=claude-haiku
export LIAR_EXTRA_PATH=/home/you/neathack/opt/node/bin  # Linux-only dir, never /mnt/*
rm -rf work && mkdir work && cp -r golden work/golden   # fix in copy, keep golden broken
set -a && . ./.env && set +a
.venv/bin/python src/agent/run.py work/golden/README.md --workdir work/golden > /tmp/before.json
.venv/bin/python src/agent/fix.py /tmp/before.json --workdir work/golden --apply
.venv/bin/python src/agent/run.py work/golden/README.md --workdir work/golden > /tmp/after.json
```

Without keys, `run.py` still works with a heuristic score (`100 * passed / total`).

Check parsing only:

```bash
.venv/bin/python src/agent/claims.py golden/README.md
```

## Configuration

| Var | Purpose | Default |
| --- | --- | ------- |
| `LITELLM_API_KEY` | OpenAI-compatible key for the 1-call verdict | `sk-test` fallback (expect `llm-error`) |
| `LITELLM_BASE_URL` | LLM endpoint | `https://litellm.vision.aivar.app/v1` (example) |
| `MODEL` | verdict model | `claude-haiku` |
| `LIAR_EXTRA_PATH` | one extra sandbox `PATH` dir, must be under `/home/` or `/tmp/` | ignored otherwise |

## Truth Score

`score = 100 * passed_commands / total_commands`. Golden fixture: before = 50 (`npm run seed` fails with `MODULE_NOT_FOUND`), after fix scaffolds `scripts/seed.js` → 100. The LLM verdict is stricter than the executor (e.g. may say `docs-fix` score 25 when commands pass but env/port/link claims are wrong) — that gap is intentional demo material.

## Sandbox safety

- Clean env: only `PATH` (default `/usr/bin:/bin` + optional `LIAR_EXTRA_PATH`), `HOME=/tmp`, `CI=1`. No host secrets leak into `subprocess.run`.
- 60s timeout per command, output truncated to last 2000 chars.
- `run.py` refuses READMEs outside CWD; `fix.py` never writes outside `--workdir`.
- `work/` is gitignored scratch; `.env` is gitignored.

## Known limitations

- No Docker; WSL env isolation + timeout only.
- `fix.py` v1 handles only the missing-`node`-file case; other lies (wrong env key, wrong port, dead link) are reported, not auto-fixed.
- Shared LLM budget: keep calls ≤1 per repo run (`fix.py` uses zero).
