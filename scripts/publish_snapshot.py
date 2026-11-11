"""Publish snapshots on watcher-data branch, avoiding Zyte auto-deploy on main."""
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
BRANCH = "watcher-data"
BODY = Path("out/latest.json").read_bytes()
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def request_json(url, method="GET", obj=None):
    body = json.dumps(obj).encode("utf-8") if obj is not None else None
    headers = {
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=25) as result:
        return json.loads(result.read().decode("utf-8"))


def put(path):
    endpoint = f"https://api.github.com/repos/{REPO}/contents/{quote(path, safe='/')}"
    sha = None
    try:
        existing = request_json(endpoint + "?ref=" + BRANCH)
        sha = existing["sha"]
    except HTTPError as error:
        if error.code != 404:
            raise
    payload = {
        "message": "data: update read-only NEU event snapshot",
        "branch": BRANCH,
        "content": base64.b64encode(BODY).decode("ascii"),
    }
    if sha:
        payload["sha"] = sha
    request_json(endpoint, "PUT", payload)
    print("published " + path)


def main():
    # No secrets or user data appear in these event status snapshots.
    put("latest.json")
    put(f"history/{DATE}.json")
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/latest.json"
    print("snapshot_url=" + url)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### Event Watcher snapshot\n[Latest JSON]({url})\n")


if __name__ == "__main__":
    main()
