#!/usr/bin/env python3
"""Fetch paper metadata from arxiv API. Stdlib only."""

import argparse
import json
import re
import ssl
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional, List

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _urlopen(url: str, timeout: int = 30, retries: int = 3):
    """urlopen with retry on 429/5xx."""
    ctx = ssl.create_default_context()
    for attempt in range(retries):
        try:
            return urllib.request.urlopen(url, timeout=timeout, context=ctx)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise


def extract_arxiv_id(input_str: str) -> Optional[str]:
    """Extract arxiv ID from URL or raw ID string."""
    patterns = [
        r"arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)",
        r"arxiv\.org/pdf/(\d{4}\.\d{4,5}(?:v\d+)?)",
        r"^(\d{4}\.\d{4,5}(?:v\d+)?)$",
    ]
    for p in patterns:
        m = re.search(p, input_str)
        if m:
            return m.group(1)
    return None


def parse_entry(entry) -> dict:
    """Parse a single Atom entry into a dict."""
    def text(tag, ns="atom"):
        el = entry.find(f"{ns}:{tag}", NS) if ns else entry.find(tag, NS)
        return el.text.strip() if el is not None and el.text else ""

    authors = [a.find("atom:name", NS).text for a in entry.findall("atom:author", NS)]

    categories = [c.get("term") for c in entry.findall("atom:category", NS)]
    primary = entry.find("arxiv:primary_category", NS)
    primary_cat = primary.get("term") if primary is not None else (categories[0] if categories else "")

    # Extract arxiv ID from the entry ID URL
    entry_id = text("id")
    arxiv_id = ""
    m = re.search(r"abs/(.+?)(?:v\d+)?$", entry_id)
    if m:
        arxiv_id = m.group(1)

    pdf_url = ""
    for link in entry.findall("atom:link", NS):
        if link.get("title") == "pdf":
            pdf_url = link.get("href", "")
            break

    return {
        "title": " ".join(text("title").split()),
        "authors": authors,
        "abstract": " ".join(text("summary").split()),
        "published": text("published"),
        "updated": text("updated"),
        "arxiv_id": arxiv_id,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
        "categories": categories,
        "primary_category": primary_cat,
    }


def fetch_by_id(arxiv_id: str) -> List[dict]:
    query = f"id_list={arxiv_id}"
    url = f"{ARXIV_API}?{query}"
    with _urlopen(url) as resp:
        tree = ET.parse(resp)
    entries = tree.getroot().findall("atom:entry", NS)
    return [parse_entry(e) for e in entries if e.find("atom:title", NS) is not None]


def fetch_by_search(query: str, max_results: int = 10, categories: List[str] = None) -> List[dict]:
    search_query = f"all:{query}"
    if categories:
        cat_filter = " OR ".join(f"cat:{c}" for c in categories)
        search_query = f"({search_query}) AND ({cat_filter})"

    params = urllib.parse.urlencode({
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{params}"
    with _urlopen(url) as resp:
        tree = ET.parse(resp)
    entries = tree.getroot().findall("atom:entry", NS)
    return [parse_entry(e) for e in entries]


def main():
    parser = argparse.ArgumentParser(description="Fetch arxiv paper metadata")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", help="Arxiv ID (e.g., 2401.12345)")
    group.add_argument("--url", help="Arxiv URL")
    group.add_argument("--search", help="Search query")
    parser.add_argument("--max", type=int, default=10, help="Max results for search")
    parser.add_argument("--categories", help="Comma-separated arxiv categories filter")
    args = parser.parse_args()

    cats = args.categories.split(",") if args.categories else None

    if args.id:
        results = fetch_by_id(args.id)
    elif args.url:
        arxiv_id = extract_arxiv_id(args.url)
        if not arxiv_id:
            print(json.dumps({"error": f"Cannot extract arxiv ID from: {args.url}"}))
            sys.exit(1)
        results = fetch_by_id(arxiv_id)
    else:
        results = fetch_by_search(args.search, args.max, cats)

    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
