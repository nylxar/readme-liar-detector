# Demo script (3 min max, faceless, captions only, OBS screen-only, mic/camera off)

## Clip 1 — Agent loop (60s): fail → fix → prove
- Card: "README Liar Detector: every README claim executed, scored, fixed."
- Terminal, repo dir. Run BEFORE on work/golden (fresh copy): score 50,
  `npm run seed` MODULE_NOT_FOUND.
- Run fix.py --apply: `scripts/seed.js` scaffolded. Re-run: score 100.
- Card: "50 → 100. Same loop on curium-core: no lies (null + links 200 + cargo PASS)."

## Clip 2 — neatlogs (60s): every step traced
- Dashboard: open BEFORE trace (WORKFLOW readme-verify, TOOL spans, LLM verdict,
  tokens/cost/latency) then AFTER trace. Narrate via captions: "fail trace found
  the missing file; pass trace verified the fix."
- Show probe trace row (TRACE_VISIBLE + TRACE_FINALIZED) briefly.
- Card with the 3 numbers (tokens, $, latency) before vs after.

## Clip 3 — Entire + cfo.ai (60s)
- Terminal: `entire graph search` top hit verify_with_llm (file:line).
- Browser: checkpoint link (ses_ed0c6afd) + `entire/` graph JSONs in repo.
- Browser: cfo.ai sheet — price floor, margin, runway. Caption (honest):
  "cfo.ai prices the scan; traces supply the true unit cost."
- End card: repo URL + "Truth Score: trust, verified."

## Build
- 3 clips → concat: ffmpeg -f concat -safe 0 -i list.txt -c copy demo.mp4
- Upload unlisted YouTube. No face, no voice, no names in metadata.
