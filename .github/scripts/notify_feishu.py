"""Send GitHub Actions status notifications to a Feishu custom bot."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request


def _sign(timestamp: str, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(string_to_sign, digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def main() -> int:
    webhook = _env("FEISHU_WEBHOOK")
    if not webhook:
        print("FEISHU_WEBHOOK is not configured; skipping Feishu notification.")
        return 0

    status = _env("CI_STATUS", "unknown")
    title = {
        "started": "GitHub Actions CI started",
        "success": "GitHub Actions CI succeeded",
        "failure": "GitHub Actions CI failed",
    }.get(status, f"GitHub Actions CI {status}")

    text = "\n".join(
        [
            title,
            f"Repo: {_env('GITHUB_REPOSITORY')}",
            f"Branch: {_env('GITHUB_REF_NAME')}",
            f"Commit: {_env('GITHUB_SHA')[:8]}",
            f"Actor: {_env('GITHUB_ACTOR')}",
            f"Workflow: {_env('GITHUB_WORKFLOW')}",
            f"Run: {_env('GITHUB_SERVER_URL')}/{_env('GITHUB_REPOSITORY')}/actions/runs/{_env('GITHUB_RUN_ID')}",
        ]
    )

    payload = {
        "msg_type": "text",
        "content": {"text": text},
    }

    secret = _env("FEISHU_SECRET")
    if secret:
        timestamp = str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = _sign(timestamp, secret)

    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"Failed to send Feishu notification: {exc}", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
