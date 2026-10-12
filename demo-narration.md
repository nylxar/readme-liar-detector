# Demo narration — exact on-screen text per shot (no voice; cards + captions)

Total ≤3:00. One continuous take. Cards from demo-cards.html (PgDn between scenes).

## Shot 1 — Problem (0:00–0:20, card 1 + README on screen)
Card text (already in demo-cards.html): "Every README claim. Executed. Scored. Fixed."
Your caption (type as terminal echo before running, or hold a card 5s):
"READMEs lie: broken commands, dead links, wrong ports. Onboarding breaks silently.
This agent runs every claim sandboxed and scores it: the Truth Score."

## Shot 2 — Live proof, golden (0:20–1:30, terminal)
One command: `.venv/bin/python src/agent/liar.py work/golden/README.md --workdir work/golden`.
Hold output: "BEFORE score=50 fixes=['scripts/seed.js'] AFTER score=100".

## Shot 3 — Live proof, real repo (1:30–1:50, terminal)
Show curium result (pre-run, scroll output): score null, links 200/200.
Caption: "Same loop on a real crate: no runnable lies, both links live, cargo check
passes default and SVG-only. Cleared innocent — no invented failures."

## Shot 4 — Traces (1:50–2:25, dashboard)
Before trace open: "Failing trace pinned the missing module: TOOL span, exit code, output."
After trace open: "Passing trace verified the scaffold. Tokens, cost, latency on screen."
One-line verdict call visible in both: docs-fix vs code-fix reasoning.

## Shot 5 — Context + business (2:25–2:50, terminal + browser)
Terminal: entire graph search top hit (verify_with_llm, file:line).
Browser: checkpoint page (ses_ed0c6afd).
Browser: business sheet. Caption: "Unit cost comes from real trace tokens; price floor follows."
End card (already in demo-cards.html): repo URL. Stop recording (≤3:00).
