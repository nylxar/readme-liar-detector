#!/usr/bin/env python3
"""Liar Detector in one command: verify -> fix -> re-verify, print the story.
Usage (keys via env; without keys: heuristic, untraced):
  .venv/bin/python src/agent/liar.py work/golden/README.md --workdir work/golden
Env: NEATLOGS_API_KEY, LITELLM_BASE_URL / LLM_BASE_URL, LITELLM_API_KEY /
LLM_API_KEY, MODEL (default claude-haiku), LIAR_EXTRA_PATH (sandbox extras).
Exit 0 when final score is 100 or null (nothing verifiable), 1 otherwise.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from run import get_client, verify_with_llm, HAS_NEATLOGS
from claims import parse_readme
from links import check_links
from sandbox import run_claim
from fix import load_package, fix_npm_missing_file

if HAS_NEATLOGS:
    import neatlogs


def verify(readme: str, workdir: str, client, model: str) -> dict:
    claims = parse_readme(readme)
    results = [run_claim(c, cwd=workdir) for c in claims["commands"]]
    verifiable = [r for r in results if "env_missing" not in r]
    passed = sum(1 for r in verifiable if r["ok"])
    score = int(100 * passed / len(verifiable)) if verifiable else None
    verdict = verify_with_llm(client, model, claims, results) if results else "no-commands"
    return {"claims": claims, "results": results, "score": score,
            "env_missing": sorted({r["env_missing"] for r in results if "env_missing" in r}),
            "link_checks": check_links(claims["links"]), "verdict": verdict}


def fix_all(before: dict, workdir: str) -> list[str]:
    pkg = load_package(workdir)
    fixes: list[str] = []
    for r in before["results"]:
        if r["ok"]:
            continue
        made = fix_npm_missing_file(r["cmd"], workdir, pkg)
        if made:
            fixes.append(made)
    return fixes


def main() -> int:
    ap = argparse.ArgumentParser(prog="liar")
    ap.add_argument("readme", help="target README.md (must be inside current directory)")
    ap.add_argument("--workdir", required=True, help="disposable repo copy to execute in")
    ap.add_argument("--json", action="store_true", help="print full JSON instead of story")
    args = ap.parse_args()

    cwd = os.path.realpath(os.getcwd())
    if os.path.commonpath([cwd, os.path.realpath(args.readme)]) != cwd:
        print("ERROR: readme must be inside current working directory.", file=sys.stderr)
        return 2

    client = get_client()
    model = os.environ.get("MODEL", "claude-haiku")

    if HAS_NEATLOGS and client is not None:
        @neatlogs.span(kind="WORKFLOW", name="readme-verify")
        def traced_verify():
            return verify(args.readme, args.workdir, client, model)
        before = traced_verify()
    else:
        before = verify(args.readme, args.workdir, client, model)

    fixes = fix_all(before, args.workdir) if before["score"] not in (100, None) else []
    after = verify(args.readme, args.workdir, client, model) if fixes else before

    if HAS_NEATLOGS and client is not None:
        try:
            neatlogs.flush()
            neatlogs.shutdown()
        except Exception as e:
            print(f"neatlogs flush warn: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps({"before": before, "fixes": fixes, "after": after}, indent=2))
    else:
        print(f"BEFORE score={before['score']} fixes={fixes or 'none'} AFTER score={after['score']}")
        print(f"verdict: {str(after['verdict'])[:300]}")
    final = after["score"]
    return 0 if final in (100, None) else 1


if __name__ == "__main__":
    sys.exit(main())
