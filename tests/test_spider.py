"""Regression checks for Scrapy 2.20+ and safe event parsing (no network)."""
import asyncio
import unittest
from scrapy.http import HtmlResponse, Request
from neu_event_watcher.spiders.event_status import EventStatusSpider
from neu_event_watcher.sources import EVENTS


class EventStatusSpiderTest(unittest.TestCase):
    def test_async_start_yields_expected_event_request(self):
        spider = EventStatusSpider()

        async def collect():
            return [req async for req in spider.start()]

        requests = asyncio.run(collect())
        self.assertEqual(len(requests), len(EVENTS))
        self.assertEqual(requests[0].url, EVENTS[0]["url"])
        self.assertEqual(requests[0].cb_kwargs["event"]["event_id"], EVENTS[0]["event_id"])

    def test_sold_out_visible_in_html(self):
        spider = EventStatusSpider()
        html = "<html><body><main><h1>Sea-Novation</h1><p>Đăng ký</p><strong>Hết vé</strong><p>CLB Dynamic NEU tổ chức một sự kiện tại hội trường A2.</p></main></body></html>"
        response = HtmlResponse(
            url=EVENTS[0]["url"],
            body=html.encode("utf-8"),
            encoding="utf-8",
            request=Request(EVENTS[0]["url"]),
        )
        result = list(spider.parse(response, EVENTS[0]))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["registration_status"], "SOLD_OUT")
        self.assertIn("hết vé", result[0]["evidence_excerpt"])


if __name__ == "__main__":
    unittest.main()
