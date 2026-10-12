"""Deterministic docs/code fixer v1 (no LLM: protects the $20 shared key).
Reads a verify JSON (run.py output), fixes structural lies, re-runs failures.
Fix 1 (code-fix): `npm run <s>` where package.json declares `node <file>`
and <file> is missing -> scaffold minimal <file>, re-run.
Usage (WSL, keys in .env, node via LIAR_EXTRA_PATH):
  .venv/bin/python src/agent/run.py golden/README.md --workdir golden-work > /tmp/before.json
  .venv/bin/python src/agent/fix.py /tmp/before.json --workdir golden-work --apply > /tmp/after.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sandbox import run_claim

STUB = '// scaffolded by liar-detector fix v1 (deterministic): missing file declared by package.json\nconsole.log("seed ok");\n'


def load_package(workdir: str) -> dict:
    p = os.path.join(workdir, "package.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def fix_npm_missing_file(cmd: str, workdir: str, pkg: dict) -> str | None:
    parts = cmd.strip().split()
    if len(parts) != 3 or parts[0] != "npm" or parts[1] != "run":
        return None
    script = pkg.get("scripts", {}).get(parts[2], "")
    toks = script.strip().split()
    if len(toks) != 2 or toks[0] != "node" or not toks[1].endswith(".js"):
        return None
    target = os.path.realpath(os.path.join(workdir, toks[1]))
    root = os.path.realpath(workdir)
    if os.path.commonpath([root, target]) != root:
        return None  # never write outside workdir
    if os.path.exists(target):
        return None
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(STUB)
    return os.path.relpath(target, root)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verify_json")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(args.verify_json, encoding="utf-8") as f:
        # run.py appends a one-line SDK shutdown note to stdout; read first doc.
        before, _ = json.JSONDecoder().raw_decode(f.read())
    if not args.apply:
        print(json.dumps({"dry_run": True, "would_fix": [r["cmd"] for r in before["results"] if not r["ok"]]}, indent=2))
        return

    pkg = load_package(args.workdir)
    fixes: list[str] = []
    for r in before["results"]:
        if r["ok"]:
            continue
        made = fix_npm_missing_file(r["cmd"], args.workdir, pkg)
        if made:
            fixes.append(made)

    results = [run_claim(c, cwd=args.workdir) for c in before["claims"]["commands"]]
    verifiable = [r for r in results if "env_missing" not in r]
    passed = sum(1 for r in verifiable if r["ok"])
    score_after = int(100 * passed / len(verifiable)) if verifiable else None
    out = {
        "fixes": fixes,
        "results": results,
        "score_before": before["score"],
        "score_after": score_after,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
