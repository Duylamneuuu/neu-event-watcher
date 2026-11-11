"""Package the NEU Event Watcher Scrapy project for Zyte Scrapy Cloud."""
from setuptools import find_packages, setup

setup(
    name="neu-event-watcher",
    version="0.1.1",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = neu_event_watcher.settings"]},
)
