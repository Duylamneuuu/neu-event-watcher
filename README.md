# NEU Event Watcher — Zyte Scrapy Cloud

Small, read-only starter crawler to monitor public registration status for NEU events. It is **not** a Facebook scraper and **not** an autonomous publisher.

## What it does

- Checks public event landing pages, currently SEA-NOVATION on Quickom.
- Detects explicit `Hết vé`, `Hết suất`, `Đóng đơn`, etc.
- Produces one item per event with UTC check time, status, evidence, page hash and review flag.
- If the page is blocked, JS-only, or missing a clear status, returns `UNCERTAIN` or skips according to robots.txt; never fabricates `OPEN`.
- No API key, no paid Zyte API, no Facebook login, no form submission, no Activepieces call.
- Stores results as Scrapy Cloud job items. Comparing across jobs / sending them to Muse is **not yet connected**.

## Where to edit the monitored URLs

Edit `neu_event_watcher/sources.py`. Add one **dedicated public event page** per event, not a page listing multiple unrelated events. Always confirm access is allowed by the site's terms and robots.txt. Don't add Facebook URLs.

## Test locally (without creating a cloud job)

```bash
python -m unittest discover -s tests -v
pip install -r requirements.txt
scrapy list
# Optional explicit spider run; may contact the public site:
scrapy crawl event_status -O observations.json
```

## Deploy by Zyte + GitHub (no terminal after code is uploaded)

1. Create a GitHub repository; put this project's **contents at the repository root** (`scrapy.cfg` must be in root).
2. In https://app.zyte.com/p/884885, open Scrapy Cloud project → **Code & Deploys → Repository → Connect to GitHub**.
3. Select the repository and deploy the default branch. Leave Auto Deploy off until validated if desired.
4. Run one `event_status` job on **1 Unit** after confirming plan/billing; inspect job Items. Do **not** enable Zyte API billing or browser rendering.
5. If your GitHub Student Pack entitlement includes schedules, set one Periodic Job (e.g. 08:00 UTC = 15:00 Asia/Bangkok); start with a single daily job, not repeated polling.

Alternative CLI, in repository root: `pip install shub && shub login && shub deploy 884885` (don't paste API keys in chat).

## Cautions

- Static Scrapy may not see content that is rendered only with JavaScript. Report `UNCERTAIN`; use Muse Browser / TinyFish to verify. This is especially relevant to booking/status widgets.
- URL response and status are a **point-in-time observation**, not guaranteed truth for another date.
- Event-specific deadline text must be matched to the same event, not to a CTV campaign in the page footer.
- No integration with Facebook, Muse or Activepieces is enabled by this template.
- Scrapy Cloud student benefit is a *hosting unit*, not unlimited paid Zyte API usage.

Official docs: https://docs.zyte.com/scrapy-cloud/usage/deployment.html
