"""README Liar Detector loop v0.1.
Trace every run with neatlogs (init + wrap + flush). Keep LLM calls <=3/repo for $20 budget.
Usage (in WSL archlinux, isolated from host creds):
  pip install -U -r requirements.txt
  export LLM_API_KEY=...
  export LLM_BASE_URL=https://your-llm-provider/v1 MODEL=claude-haiku
  python -m neatlogs doctor --local --json
  python -m neatlogs doctor --probe --json
  python src/agent/run.py golden/README.md --workdir golden
Sandbox: clean env (PATH/HOME/CI only), timeout 60s, cwd=repo copy. Never passes host secrets.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from claims import parse_readme
from links import check_links
from sandbox import run_claim

try:
    import neatlogs
    HAS_NEATLOGS = True
except ImportError:
    HAS_NEATLOGS = False


def _load_dotenv() -> None:
    """Load .env from CWD only (never committed, gitignored). Real env wins."""
    try:
        with open(".env", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


def get_client():
    if not HAS_NEATLOGS:
        return None
    _load_dotenv()
    key = os.environ.get("NEATLOGS_API_KEY", "")
    if not key or key.startswith("paste-"):
        print("WARN: NEATLOGS_API_KEY missing, running untraced.", file=sys.stderr)
        return None
    if key.startswith("nlw_"):
        print("ERROR: use Project API key, not nlw_ HTTP key.", file=sys.stderr)
        sys.exit(1)
    # Latest Python SDK per https://docs.neatlogs.com/sdk/python + agent prompt:
    # init once, regional endpoint, task workflow name, key from env only.
    neatlogs.init(
        api_key=key,
        endpoint="https://ingest.neatlogs.com",
        workflow_name="readme-verify",
    )
    from openai import OpenAI
    base = os.environ.get("LLM_BASE_URL") or os.environ.get("LITELLM_BASE_URL") or None
    okey = os.environ.get("LLM_API_KEY") or os.environ.get("LITELLM_API_KEY") or "sk-test"
    client = OpenAI(api_key=okey, base_url=base) if base else OpenAI(api_key=okey)
    return neatlogs.wrap(client)


def verify_with_llm(client, model: str, claims: dict, results: list) -> str:
    """One LLM call max: docs-fix vs code-fix + Truth Score reasoning."""
    if client is None:
        return "untraced-verdict: manual review (no LLM key)"
    prompt = (
        "You verify README claims. Given claims and sandbox results, output JSON "
        '{"score":0-100,"verdict":"docs-fix|code-fix|ok","reason":short}. '
        f"CLAIMS={json.dumps(claims)[:2000]} RESULTS={json.dumps(results)[:3000]}"
    )
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content
    except Exception as e:
        # Shared $20 key can rate-limit or exhaust; record instead of crashing.
        return f"llm-error: {type(e).__name__}: {str(e)[-300:]}"


def run_all(readme: str, workdir: str, client, model: str) -> dict:
    claims = parse_readme(readme)
    results = [run_claim(c, cwd=workdir) for c in claims["commands"]]
    # env-missing (absent toolchain) is unverifiable, not a lie: exclude it.
    verifiable = [r for r in results if "env_missing" not in r]
    passed = sum(1 for r in verifiable if r["ok"])
    # No verifiable claims (e.g. README with no runnable commands and full
    # toolchain present elsewhere): null, not 0. 0 would cry "all lies".
    score = int(100 * passed / len(verifiable)) if verifiable else None
    verdict = verify_with_llm(client, model, claims, results) if results else "no-commands"
    return {"claims": claims, "results": results, "score": score,
            "env_missing": sorted({r["env_missing"] for r in results if "env_missing" in r}),
            "link_checks": check_links(claims["links"]), "verdict": verdict}


if HAS_NEATLOGS:
    @neatlogs.span(kind="TOOL", tool_name="sandbox_run")
    def traced_claim(cmd: str, workdir: str) -> dict:
        return run_claim(cmd, cwd=workdir)

    @neatlogs.span(kind="WORKFLOW", name="readme-verify")
    def traced_run(readme: str, workdir: str, client, model: str) -> dict:
        claims = parse_readme(readme)
        results = [traced_claim(c, workdir) for c in claims["commands"]]
        verifiable = [r for r in results if "env_missing" not in r]
        passed = sum(1 for r in verifiable if r["ok"])
        score = int(100 * passed / len(verifiable)) if verifiable else None
        verdict = verify_with_llm(client, model, claims, results) if results else "no-commands"
        return {"claims": claims, "results": results, "score": score,
                "env_missing": sorted({r["env_missing"] for r in results if "env_missing" in r}),
                "link_checks": check_links(claims["links"]), "verdict": verdict}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("readme", help="path to target README.md (inside CWD only)")
    ap.add_argument("--workdir", default=".", help="sandbox cwd (repo copy, no secrets)")
    args = ap.parse_args()

    # Scope guard per agent prompt: never instrument outside CWD.
    cwd = os.path.realpath(os.getcwd())
    if os.path.commonpath([cwd, os.path.realpath(args.readme)]) != cwd:
        print("ERROR: readme must be inside current working directory.", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    model = os.environ.get("MODEL", "claude-haiku")
    if HAS_NEATLOGS and client is not None:
        out = traced_run(args.readme, args.workdir, client, model)
    else:
        out = run_all(args.readme, args.workdir, client, model)
    print(json.dumps(out, indent=2))

    if HAS_NEATLOGS and client is not None:
        try:
            neatlogs.flush()
            neatlogs.shutdown()
        except Exception as e:
            print(f"neatlogs flush warn: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
