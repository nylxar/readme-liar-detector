"""Isolated command runner. MUST run in WSL/EC2, never on host with secrets.
- timeout 60s, clean env, cwd=target repo copy only, no host PATH.
- LIAR_EXTRA_PATH may prepend ONE Linux/macOS-only dir (node, etc). It must
  live under /home/, /tmp/, or /Users/; anything else is ignored. Never set
  it to /mnt/*.
"""
import os
import subprocess

_BASE_PATH = "/usr/bin:/bin"


def _sandbox_path() -> str:
    extra = os.environ.get("LIAR_EXTRA_PATH", "").rstrip("/")
    allowed = extra in ("/tmp", "/home", "/Users") or extra.startswith(("/home/", "/tmp/", "/Users/"))
    if extra and os.path.isdir(extra or "/") and allowed:
        return extra + ":" + _BASE_PATH
    return _BASE_PATH


SAFE_ENV = {"PATH": _sandbox_path(), "HOME": "/tmp", "CI": "1"}

def run_claim(cmd: str, cwd: str, timeout: int = 60) -> dict:
    binary = cmd.strip().split()[0] if cmd.strip() else ""
    try:
        p = subprocess.run(
            cmd, shell=True, cwd=cwd, env=SAFE_ENV,
            capture_output=True, text=True, timeout=timeout,
        )
        out = (p.stdout + p.stderr)[-2000:]
        res: dict = {"cmd": cmd, "ok": p.returncode == 0, "code": p.returncode, "output": out}
    except subprocess.TimeoutExpired as e:
        res = {"cmd": cmd, "ok": False, "code": 124, "output": f"TIMEOUT after {timeout}s: {str(e)[-500:]}"}
    except Exception as e:
        res = {"cmd": cmd, "ok": False, "code": 1, "output": f"RUNNER_ERROR: {e}"[-1000:]}
    # 127 + command-not-found means the TOOLCHAIN is absent, not that the
    # README lies. Mark it so scoring/verdicts don't count it as a lie.
    if not res["ok"] and res["code"] == 127 and "command not found" in res["output"]:
        res["env_missing"] = binary
    return res
