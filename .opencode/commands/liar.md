---
description: Verify a repo README for lies, fix, and re-verify (Truth Score)
---

Run the README liar detector end to end on a target repo. Keys come from the
project `.env` (auto-loaded); nothing is committed.

1. Copy the target into scratch (never fix originals):
   `rm -rf work/target && mkdir -p work && cp -r <target> work/target`
2. If the target needs node: `export LIAR_EXTRA_PATH=<node-bin-dir>` (must be
   under `/home/`, `/tmp/`, or `/Users/`).
3. Run one command and report the story line:
   `.venv/bin/python src/agent/liar.py work/target/README.md --workdir work/target`
4. Report: BEFORE score, fixes applied, AFTER score, verdict (docs-fix |
   code-fix | ok), link check results, and the neatlogs trace workflow name
   (`readme-verify`) for evidence.
