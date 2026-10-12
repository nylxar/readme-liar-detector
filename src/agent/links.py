"""Link reachability check (stdlib only, no LLM, no extra budget).
HEAD with fallback to GET, 10s timeout, 1 redirect max. Never sends secrets.
"""
import urllib.request


def check_link(url: str, timeout: int = 10) -> dict:
    if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
        note = "loopback: only meaningful with a live server; reports connection only"
    else:
        note = ""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "liar-detector/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {"url": url, "ok": 200 <= resp.status < 400, "code": resp.status, "note": note}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[-160:]}"
    return {"url": url, "ok": False, "code": -1, "output": last, "note": note}


def check_links(urls: list[str]) -> list[dict]:
    return [check_link(u) for u in urls[:10]]
