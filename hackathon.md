# Project: readme-liar-detector
# One sentence: Agent that proves README claims by running them in a sandbox and opens a minimal fix PR.
# Problem: READMEs lie (bad commands, wrong env keys, wrong ports, dead links); onboarding breaks.

# Team: solo (handle to publish later)

# Stack:
# - Python + openai SDK via LiteLLM ($20 budget, OpenAI-compatible)
# - neatlogs SDK 1.4.25 (init + wrap + flush, Project API key not nlw_ key)
# - Entire CLI (checkpoints + entire-graph), Trails optional
# - cfo.ai (pricing/costs/revenue/runway, via cfo.ai/neathacks)
# - Crustdata promo NEATLOGS-OCT2026 (external claim check, max ~50 credits)
# - Sandbox: WSL archlinux now, EC2 t3.micro us-east-1 later ($25 compute only, no Bedrock)

# Build log:
# 2026-10-10: Scaffolded loop (parse -> sandbox try -> graph lookup -> fix -> re-run -> Truth Score). No keys committed. Next: neatlogs doctor --probe, first trace, Entire enable + first checkpoint.
# 2026-10-10 (WSL archlinux, isolated ~/neathack, py3.13 venv via uv): neatlogs 1.4.26 + openai installed.
# - doctor --local PASS, claims.py parse OK (2 cmds, env, ports, links).
# - Found + fixed WSL PATH leak (Windows npm ran, wrote to host npm-cache). Sandbox now PATH=/usr/bin:/bin only. Re-ran untraced: score 50, no host paths.
# - doctor --probe PASS (TRACE_VISIBLE + TRACE_FINALIZED). Key via WSL env only, never in repo.
# 2026-10-10: User pasted keys into WSL .env.example by mistake. Moved to chmod 600 .env (gitignored), restored .env.example placeholders, removed stray line. Verified no key names/values in outputs.
# 2026-10-10: First TRACED run (claude-haiku via LiteLLM, 1 call): score 50 heuristic, verdict docs-fix score 25. WORKFLOW readme-verify + TOOL spans exported, flush+shutdown clean.
# 2026-10-11: SECURITY: user pasted real keys into Windows .env.example. Replaced with placeholders. Keys live only in WSL .env (chmod 600). Recommend rotating neatlogs project key after hackathon; LiteLLM key is shared — ask organizers if rotation needed.
# 2026-10-11: Node v22.19.0 in WSL ~/neathack/opt (no sudo). Golden reworked: package.json seed -> missing scripts/seed.js (real MODULE_NOT_FOUND fail).
# 2026-10-11: Built fix.py (deterministic code-fix, no LLM) + links.py (stdlib HEAD/GET). BEFORE score 50 traced, fix scaffolded scripts/seed.js, AFTER score 100 traced. LLM verdicts 25/25 docs-fix (stricter than executor — demo material).
# 2026-10-11: GitHub nylxar/readme-liar-detector held stale WSL junk (main). Force-pushed Windows master (996dca4), default branch -> master, deleted main. Secret scan 0 hits. Entire sync pending (up to ~1h).
# 2026-10-12: Real-target test on curium-core (Rust): found parser ran rust blocks as shell (fixed: language-aware blocks), link regex captured code junk (fixed + rstrip), missing toolchain counted as lie (fixed: env_missing exclusion). Node via LIAR_EXTRA_PATH; Rust 1.99 via rustup minimal. cargo check default features: PASS.
# 2026-10-12: BREAKTHROUGH: v1 session ses_ed0c6a recording (sh fix worked). Relinking.
# Cost table (fill from dashboard trace stats):
# | run | tokens in/out | $ | latency | score |
# | before (fail) | ? | ? | ? | 50 |
# | after (pass) | ? | ? | ? | 100 |
# | fix (no LLM) | 0 | 0 | ? | 50 -> 100 |

# Demo: URL + instructions TBD (faceless, 3x60s OBS clips, captions only)

# Known limitations:
# - No Docker on host; WSL isolation only + timeout 60s. No secrets in sandbox env.
# - LiteLLM budget shared; keep LLM calls <=3 per repo.
# - Entire/Trails needs GitHub org admin + sync up to 1h.

# Submission: pending
# - [ ] 2 neatlogs traces (fail vs pass) with cost/latency
# - [ ] Entire checkpoint link + ID + graph json in /entire
# - [ ] cfo.ai business plan export in /cfo
# - [ ] Demo <=3min covering architecture/implementation/runtime/reasoning/result for all three
# - [ ] Public repo, commits during hackathon
# - [ ] X quote post Oct 12 7:00-11:55 PM IST
# 2026-10-12: Checkpoint test — appended-line probe, session kept open.
