#!/bin/sh
# Judge-proof quickstart: no keys, no network beyond pip, ~2 minutes.
# Linux, macOS, or WSL. Creates throwaway copies; never touches your files.
set -e
cd "$(dirname "$0")"
PY=python3
command -v "$PY" >/dev/null || { echo "need python3 (>=3.10)"; exit 1; }
PYVER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
case "$PYVER" in
  3.10|3.11|3.12|3.13) ;;
  *) echo "python $PYVER unsupported: neatlogs needs 3.10-3.13 (got $PYVER)."; echo "Use: uv venv --python 3.13 .venv  OR  python3.13 -m venv .venv"; exit 1 ;;
esac
"$PY" -m venv .qs-venv
.qs-venv/bin/pip install -q -r requirements.txt
echo "--- parse ---"
.qs-venv/bin/python src/agent/claims.py golden/README.md
echo "--- verify (untraced, heuristic score) ---"
rm -rf work/judge && mkdir -p work && cp -r golden work/judge
env -u NEATLOGS_API_KEY .qs-venv/bin/python src/agent/run.py work/judge/README.md --workdir work/judge
