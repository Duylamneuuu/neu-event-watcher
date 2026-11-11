"""One cautious, read-only collection pass (no Zyte API calls)."""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from neu_event_watcher.sources import EVENTS

OUT = Path("out/latest.json")


def main():
    now = datetime.now(timezone.utc)
    due, ended = [], []
    for event in EVENTS:
        try:
            when = datetime.fromisoformat(event["event_datetime"])
        except (ValueError, KeyError):
            when = None
        if when is not None and now >= when.astimezone(timezone.utc):
            ended.append({
                **event,
                "checked_at_utc": now.isoformat(),
                "registration_status": "EVENT_ENDED",
                "status_confidence": "event_datetime_passed",
                "manual_review_required": False,
                "network_request_sent": False,
            })
        else:
            due.append(event)

    scraped = []
    crawl_return_code = None
    crawl_error = None
    if due:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "records.jsonl"
            command = [sys.executable, "-m", "scrapy", "crawl", "event_status",
                       "-O", str(path)]
            try:
                result = subprocess.run(command, capture_output=True, text=True,
                                        timeout=160, check=False)
                crawl_return_code = result.returncode
                if result.returncode:
                    crawl_error = "Scrapy process exited with code " + str(result.returncode)
                    print("::warning::" + crawl_error, flush=True)
                if path.exists():
                    for line in path.read_text(encoding="utf-8").splitlines():
                        if line.strip():
                            try:
                                scraped.append(json.loads(line))
                            except json.JSONDecodeError:
                                print("::warning::Malformed JSONL record", flush=True)
            except subprocess.TimeoutExpired:
                crawl_error = "Scrapy exceeded 160 seconds"
                print("::warning::" + crawl_error, flush=True)

    result_by_id = {item.get("event_id"): item for item in scraped if item.get("event_id")}
    complete = list(ended)
    for event in due:
        item = result_by_id.get(event["event_id"])
        if item:
            complete.append(item)
        else:
            complete.append({
                **event,
                "checked_at_utc": now.isoformat(),
                "registration_status": "UNCERTAIN",
                "status_confidence": "no_record_robots_or_dynamic_or_error",
                "manual_review_required": True,
                "network_request_sent": True,
                "note": "No rendered record returned; verify manually with organizer.",
            })

    report = {
        "schema_version": 1,
        "generated_at_utc": now.isoformat(),
        "execution_environment": "github_actions",
        "scrapy_cloud_job": False,
        "sources_configured": len(EVENTS),
        "crawl_attempted": bool(due),
        "crawl_exit_code": crawl_return_code,
        "crawl_error": crawl_error,
        "events": complete,
        "note": "Read-only evidence; never publish an OPEN claim from an unverified source.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"snapshot={OUT} events={len(complete)} "
          f"statuses={[item['registration_status'] for item in complete]}")
    if due and not scraped:
        print("::warning::No accessible items; marked UN​CERTAIN for manual review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
