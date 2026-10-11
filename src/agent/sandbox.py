"""Isolated command runner. MUST run in WSL/EC2, never on host with secrets.
- timeout 60s, clean env, cwd=target repo copy only, no host PATH.
- LIAR_EXTRA_PATH may prepend ONE Linux-only dir (node, etc). It must live
  under /home/ or /tmp; anything else is ignored. Never set it to /mnt/*.
"""
import os
import subprocess

_BASE_PATH = "/usr/bin:/bin"


def _sandbox_path() -> str:
    extra = os.environ.get("LIAR_EXTRA_PATH", "")
    if extra and os.path.isdir(extra) and (extra.startswith("/home/") or extra.startswith("/tmp/")):
        return extra + ":" + _BASE_PATH
    return _BASE_PATH


SAFE_ENV = {"PATH": _sandbox_path(), "HOME": "/tmp", "CI": "1"}

def run_claim(cmd: str, cwd: str, timeout: int = 60) -> dict:
    try:
        p = subprocess.run(
            cmd, shell=True, cwd=cwd, env=SAFE_ENV,
            capture_output=True, text=True, timeout=timeout,
        )
        out = (p.stdout + p.stderr)[-2000:]
        return {"cmd": cmd, "ok": p.returncode == 0, "code": p.returncode, "output": out}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "ok": False, "code": 124, "output": f"TIMEOUT after {timeout}s: {str(e)[-500:]}"}
    except Exception as e:
        return {"cmd": cmd, "ok": False, "code": 1, "output": f"RUNNER_ERROR: {e}"[-1000:]}
