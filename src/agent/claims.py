"""Parse README into verifiable claims: commands, env keys, ports, links."""
import re
from pathlib import Path

CMD_RE = re.compile(r"```(?:bash|sh|shell)?\n(.*?)```", re.S)
INLINE_RE = re.compile(r"`(npm run [^`]+|npm install|pip install[^`]*|python[^`]*|node[^`]+)`")
ENV_RE = re.compile(r"\b([A-Z][A-Z0-9_]{3,})\b")
PORT_RE = re.compile(r"(?::|port\s+|localhost:)(\d{2,5})", re.I)
LINK_RE = re.compile(r"https?://[^\s\)\]]+")

def parse_readme(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    blocks = [m.group(1) for m in CMD_RE.finditer(text)]
    cmds = []
    for b in blocks:
        for line in b.splitlines():
            line = line.strip().lstrip("$ ").strip()
            if line and not line.startswith("#"):
                cmds.append(line)
    inline = [m.group(1).strip() for m in INLINE_RE.finditer(text)]
    for c in inline:
        if c not in cmds:
            cmds.append(c)
    # Backticked ALL_CAPS tokens are code (env keys); prose stays out.
    ticked = re.findall(r"`([A-Z][A-Z0-9_]{3,})`", text)
    # Env keys only from code (blocks + inline), never prose: avoids
    # false positives like NOT/ONLY/PATH from sentences.
    code_text = "\n".join(blocks + inline + ticked)
    return {
        "commands": cmds[:10],  # cap for $20 budget / time
        "env_keys": sorted(set(ENV_RE.findall(code_text)))[:20],
        "ports": sorted(set(PORT_RE.findall(text)))[:10],
        "links": sorted(set(LINK_RE.findall(text)))[:10],
    }

if __name__ == "__main__":
    import sys, json
    print(json.dumps(parse_readme(sys.argv[1] if len(sys.argv) > 1 else "golden/README.md"), indent=2))
