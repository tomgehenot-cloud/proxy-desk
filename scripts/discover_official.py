#!/usr/bin/env python3
"""Discover official ZZZ event announcements without inventing deadlines."""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

URL = "https://zenless.hoyoverse.com/en-us/news/cate/"
OUTPUT = Path("feed/discovered.json")
KEYWORDS = ("event", "login", "check-in", "version", "update", "program", "reward")
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.parts = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.parts = []
    def handle_data(self, data):
        if self.href is not None:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.links.append((self.href, " ".join(self.parts).strip()))
            self.href = None

def collect():
    req = urllib.request.Request(URL, headers={"User-Agent": "ProxyDeskDiscovery/1.0 (+github-actions)", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=25) as response:
        html = response.read(3_000_000).decode("utf-8", errors="replace")
    parser = Links()
    parser.feed(html)
    items = {}
    for href, label in parser.links:
        full = urljoin(URL, href)
        parsed = urlparse(full)
        if parsed.netloc != "zenless.hoyoverse.com" or not re.search(r"/news/\d+", parsed.path):
            continue
        label = " ".join(label.split())
        if len(label) < 10 or not any(k in label.lower() for k in KEYWORDS):
            continue
        items[full.split("?")[0]] = {"title": label[:220], "url": full.split("?")[0], "status": "review_required"}
    return sorted(items.values(), key=lambda x: x["url"], reverse=True)[:100]

def main():
    existing = {}
    if OUTPUT.exists():
        try:
            existing = json.loads(OUTPUT.read_text("utf-8"))
        except (ValueError, OSError):
            pass
    previous = {a["url"]: a for a in existing.get("announcements", []) if "url" in a}
    try:
        current = collect()
    except Exception as exc:
        print("Discovery unavailable: " + repr(exc))
        raise SystemExit(1)
    if not current:
        print("No usable official links detected; preserving existing state.")
        raise SystemExit(1)
    updated = []
    for item in current:
        old = previous.get(item["url"], {})
        updated.append({**item, "first_seen": old.get("first_seen") or datetime.now(timezone.utc).date().isoformat()})
    content = {"source": URL, "status": "discovery_only_unverified", "announcements": updated}
    if existing.get("announcements") != updated:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print(f"Updated discovered articles: {len(updated)}")
    else:
        print("No changes")

if __name__ == "__main__":
    main()
