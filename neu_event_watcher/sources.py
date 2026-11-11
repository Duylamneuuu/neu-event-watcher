"""Seed public event pages. Add only dedicated pages with public status text.

Do not add Facebook URLs: Scrapy Cloud hosting does not grant Facebook access.
Keep each event distinct, to prevent mixing workshop and CTV deadlines.
"""

EVENTS = [
    {
        'event_id': 'sea-novation-2026',
        'event_name': 'SEA-NOVATION — Can Business Save Nature?',
        'organizer': 'CLB Khởi nghiệp Sáng tạo Dynamic NEU',
        'url': 'https://quickom.net/event/sea-novation-7179',
        'event_datetime': '2026-11-12T18:30:00+07:00',
        'registration_deadline_original': '2026-11-11',
    },
]
