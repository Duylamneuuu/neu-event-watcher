"""Read only public event status; publish observations, never actions."""
from datetime import datetime, timezone
from urllib.parse import urlparse

import scrapy
from neu_event_watcher.sources import EVENTS
from neu_event_watcher.status_rules import classify_status, fingerprint


class EventStatusSpider(scrapy.Spider):
    name = 'event_status'
    handle_httpstatus_list = [401, 403, 404, 429]

    def start_requests(self):
        for event in EVENTS:
            url = event['url']
            if urlparse(url).scheme != 'https':
                self.logger.warning('Skipping non-HTTPS URL: %s', url)
                continue
            yield scrapy.Request(url, callback=self.parse, errback=self.on_failure,
                                 cb_kwargs={'event': event}, dont_filter=True)

    def parse(self, response, event):
        body_parts = response.xpath(
            '//body//text()[not(ancestor::script) and not(ancestor::style) and '
            'not(ancestor::noscript) and not(ancestor::svg)]'
        ).getall()
        raw = ' '.join(t.strip() for t in body_parts if t.strip())
        normalized = ' '.join(raw.split())
        status, evidence, confidence = classify_status(normalized)
        if response.status != 200:
            status, confidence = 'UNCERTAIN', 'http_error'
        elif len(normalized) < 80:
            status, confidence = 'UNCERTAIN', 'not_enough_rendered_text'
        links = [response.urljoin(href) for href in response.css('a[href]::attr(href)').getall()]
        # Links are hints only: do not follow form pages and NEVER submit registration.
        registration_links = list(dict.fromkeys(x for x in links if any(
            needle in x.lower() for needle in ('forms.gle/', 'docs.google.com/forms/',
                                                'quickom.net/', 'fillout.com/', 'bit.ly/'))))[:10]
        yield {
            **event,
            'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'final_url': response.url,
            'http_status': response.status,
            'registration_status': status,
            'status_confidence': confidence,
            'evidence_excerpt': evidence[:400],
            'registration_links': registration_links,
            'content_hash_sha256': fingerprint(normalized),
            'page_text_length': len(normalized),
            'manual_review_required': status == 'UNCERTAIN',
            'note': 'Snapshot only; verify with organizer and compare future jobs before updating a digest.',
        }

    def on_failure(self, failure):
        event = failure.request.cb_kwargs.get('event', {})
        yield {
            **event,
            'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'registration_status': 'UNCERTAIN',
            'status_confidence': 'network_error',
            'error': str(failure.value)[:250],
            'manual_review_required': True,
        }
