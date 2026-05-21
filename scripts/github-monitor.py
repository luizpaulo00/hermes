#!/usr/bin/env python3
"""Monitor GitHub repo state and print only relevant changes.

Safe for Hermes cron no_agent mode: empty stdout means no notification.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = os.environ.get("GITHUB_MONITOR_OWNER", "luizpaulo00")
REPO = os.environ.get("GITHUB_MONITOR_REPO", "hermes")
STATE_DIR = Path(os.environ.get("GITHUB_MONITOR_STATE_DIR", "/home/luiz/.hermes/state"))
STATE_PATH = STATE_DIR / f"github-monitor-{OWNER}-{REPO}.json"
ENV_PATH = Path(os.environ.get("HERMES_ENV_PATH", "/home/luiz/.hermes/.env"))
API = "https://api.github.com"


def load_env_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    if token:
        return token.strip().strip('"').strip("'")
    if not ENV_PATH.exists():
        return None
    for line in ENV_PATH.read_text(errors="ignore").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() in {"GITHUB_TOKEN", "GITHUB_PAT"}:
            value = value.strip().strip('"').strip("'")
            if value and value != "[REDACTED]":
                return value
    return None


def api_get(path: str, token: str, params: dict | None = None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "hermes-github-monitor",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"GitHub API HTTP {exc.code} em {path}: {body}") from exc


def compact_run(run: dict) -> dict:
    return {
        "id": run.get("id"),
        "name": run.get("name"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_branch": run.get("head_branch"),
        "head_sha": (run.get("head_sha") or "")[:12],
        "url": run.get("html_url"),
    }


def main() -> int:
    token = load_env_token()
    if not token:
        print("⚠️ Monitor GitHub: sem GITHUB_TOKEN/GITHUB_PAT em ~/.hermes/.env")
        return 0

    repo = api_get(f"/repos/{OWNER}/{REPO}", token)
    branch_name = repo.get("default_branch", "main")
    branch = api_get(f"/repos/{OWNER}/{REPO}/branches/{branch_name}", token)
    issues_raw = api_get(f"/repos/{OWNER}/{REPO}/issues", token, {"state": "open", "per_page": 20})
    prs_raw = api_get(f"/repos/{OWNER}/{REPO}/pulls", token, {"state": "open", "per_page": 20})
    runs_raw = api_get(f"/repos/{OWNER}/{REPO}/actions/runs", token, {"per_page": 5})

    issues = [i for i in issues_raw if "pull_request" not in i]
    prs = prs_raw
    runs = [compact_run(r) for r in runs_raw.get("workflow_runs", [])]
    latest_run = runs[0] if runs else None

    state = {
        "repo": f"{OWNER}/{REPO}",
        "default_branch": branch_name,
        "branch_sha": branch.get("commit", {}).get("sha", ""),
        "open_issues": sorted(i.get("number") for i in issues),
        "open_prs": sorted(p.get("number") for p in prs),
        "latest_run": latest_run,
        "checked_at": int(time.time()),
    }

    old = None
    if STATE_PATH.exists():
        try:
            old = json.loads(STATE_PATH.read_text())
        except Exception:
            old = None

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))
    STATE_PATH.chmod(0o600)

    lines: list[str] = []
    if old is None:
        lines.append("✅ Monitor GitHub ativado")
        lines.append(f"Repo: {OWNER}/{REPO}")
        lines.append(f"Branch: {branch_name} @ {state['branch_sha'][:12]}")
        lines.append(f"Issues abertas: {len(issues)}")
        lines.append(f"PRs abertos: {len(prs)}")
        if latest_run:
            lines.append(
                f"Último workflow: {latest_run['name']} — {latest_run['conclusion'] or latest_run['status']}"
            )
    else:
        if state["branch_sha"] != old.get("branch_sha"):
            lines.append(f"🔔 GitHub: branch `{branch_name}` mudou")
            lines.append(f"Antes: {(old.get('branch_sha') or '')[:12]}")
            lines.append(f"Agora: {state['branch_sha'][:12]}")
        old_issues = set(old.get("open_issues", []))
        new_issues = set(state["open_issues"])
        opened_issues = sorted(new_issues - old_issues)
        closed_issues = sorted(old_issues - new_issues)
        if opened_issues or closed_issues:
            lines.append(f"Issues: +{opened_issues or []} -{closed_issues or []}")
        old_prs = set(old.get("open_prs", []))
        new_prs = set(state["open_prs"])
        opened_prs = sorted(new_prs - old_prs)
        closed_prs = sorted(old_prs - new_prs)
        if opened_prs or closed_prs:
            lines.append(f"PRs: +{opened_prs or []} -{closed_prs or []}")
        old_run = old.get("latest_run") or {}
        if latest_run and latest_run.get("id") != old_run.get("id"):
            lines.append(
                f"Workflow novo: {latest_run['name']} — {latest_run['conclusion'] or latest_run['status']}"
            )
            if latest_run.get("url"):
                lines.append(latest_run["url"])
        elif latest_run and latest_run.get("conclusion") in {"failure", "cancelled", "timed_out"}:
            if latest_run.get("conclusion") != old_run.get("conclusion"):
                lines.append(f"⚠️ Workflow com problema: {latest_run['name']} — {latest_run['conclusion']}")
                if latest_run.get("url"):
                    lines.append(latest_run["url"])

    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        msg = str(exc).replace(load_env_token() or "", "[REDACTED]")
        print(f"⚠️ Monitor GitHub falhou: {msg}")
        raise SystemExit(0)
