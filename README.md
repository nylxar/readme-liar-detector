# readme-liar-detector

Agent that proves README claims by running them sandboxed. Outputs Truth Score 0-100 + minimal fix.

## 1. Setup (you already checked in)

- neatlogs: sign up at `https://app.neatlogs.com`, project API key (top one, not `nlw_`) -> `NEATLOGS_API_KEY`. Guide: `https://neatlogs.com/hackathon/neatlogs-setup-guide.html`. Verify: `python -m neatlogs doctor --probe` (want TRACE_VISIBLE + TRACE_FINALIZED PASS), traces in Traces tab.
- Entire: `https://hack.entire.io/neathacks-2026/` - Sign in with GitHub, org admin imports repo, `entire enable --agent <name>`, commit -> checkpoint, `entire checkpoint list`. Include checkpoint link + ID in submission.
- cfo.ai: `https://cfo.ai/neathacks` (card required, cancel immediately in Settings->Billing), credits added by team. Export pricing/costs/revenue/runway.
- Crustdata: promo `NEATLOGS-OCT2026` at `https://app.crustdata.com` (email signup, not Google), 5000 credits.
- Models: LiteLLM key from `/hackathon/models` (`https://litellm.vision.aivar.app/v1`, $20 shared budget). Default `MODEL=claude-haiku`, 1 LLM call per repo. AWS $25 us-east-1 compute only, no Bedrock.

## 2. Run isolated (distrust host)

All runs in WSL `archlinux`, never on Windows with secrets. Keys live ONLY in WSL `.env` (`chmod 600`, gitignored). Never paste keys into `.env.example` (it commits).

```bash
cp -r readme-liar-detector ~/neathack/
cd ~/neathack/readme-liar-detector
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -U -r requirements.txt
printf 'NEATLOGS_API_KEY=...\nLITELLM_API_KEY=...\n' > .env  # real keys, never commit
export LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1 MODEL=claude-haiku
export LIAR_EXTRA_PATH=/home/you/neathack/opt/node/bin  # Linux-only dir, never /mnt/*
rm -rf work && mkdir work && cp -r golden work/golden   # fix in copy, keep golden broken
set -a && . ./.env && set +a
.venv/bin/python src/agent/run.py work/golden/README.md --workdir work/golden > /tmp/before.json
.venv/bin/python src/agent/fix.py /tmp/before.json --workdir work/golden --apply
.venv/bin/python src/agent/run.py work/golden/README.md --workdir work/golden > /tmp/after.json
```

`work/` is gitignored fix scratch. Sandbox: clean env, 60s timeout, CWD guard, `LIAR_EXTRA_PATH` must be under `/home/` or `/tmp/`.

## 3. Evidence

- `traces/`: 2 neatlogs links (fail score 50 vs pass score 100) + tokens/cost
- `entire/`: graph json + checkpoint ID/link
- `cfo/`: business plan export (pending decision)
- `hackathon.md`: build log
