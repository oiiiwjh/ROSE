#!/usr/bin/env python3
"""Fetch recent papers from arxiv. Two modes:
  1) --mode list: scrape arxiv listing page → save CSV (fast, no per-paper requests)
  2) --mode detail: read CSV, batch-fetch alphaxiv overviews for selected IDs → save JSON

Stdlib only, no external dependencies.
"""

import argparse
import csv
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List, Optional


def _urlopen(url: str, timeout: int = 60, retries: int = 3):
    ctx = ssl.create_default_context()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ROSE/1.0"})
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise


# ── Mode 1: List (scrape arxiv HTML listing) ────────────────────────────

def scrape_arxiv_listing(categories: List[str], days: int = 2, max_results: int = 250) -> List[dict]:
    """Scrape arxiv recent listing pages to get paper titles, IDs, and subjects.
    This avoids the slow/unreliable arxiv API and gets data in one request."""
    results = []
    seen_ids = set()

    for cat in categories:
        url = f"https://arxiv.org/list/{cat}/recent?skip=0&show={max_results}"
        try:
            with _urlopen(url, timeout=60) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"Warning: failed to fetch {cat}: {e}", file=sys.stderr)
            continue

        # Parse arxiv IDs and titles
        ids = re.findall(r'arXiv:(\d{4}\.\d{4,5})', html)
        titles = re.findall(
            r'<span class=["\']descriptor["\']>Title:</span>\s*(.*?)\s*</div>',
            html, re.DOTALL
        )
        subjects = re.findall(r'primary-subject">(.*?)</span>', html)

        # Parse authors
        author_blocks = re.findall(r"<div class=['\"]list-authors['\"][^>]*>(.*?)</div>", html, re.DOTALL)

        for i in range(min(len(ids), len(titles))):
            aid = ids[i]
            if aid in seen_ids:
                continue
            seen_ids.add(aid)

            title = re.sub(r'\s+', ' ', titles[i]).strip()
            subj = subjects[i].strip() if i < len(subjects) else ""

            # Extract author names
            authors = []
            if i < len(author_blocks):
                authors = re.findall(r'>([^<]+)</a>', author_blocks[i])
                authors = [a.strip() for a in authors if a.strip()]

            results.append({
                "arxiv_id": aid,
                "title": title,
                "authors": authors[:5],  # keep first 5
                "primary_category": subj,
                "url": f"https://arxiv.org/abs/{aid}",
            })

    return results


def fetch_via_api(categories: List[str], days: int = 2, max_results: int = 100) -> List[dict]:
    """Fallback: fetch via arxiv API (includes abstracts but slower/less reliable)."""
    NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    date_range = f"[{start.strftime('%Y%m%d')}0000 TO {end.strftime('%Y%m%d')}2359]"

    params = urllib.parse.urlencode({
        "search_query": f"({cat_query}) AND submittedDate:{date_range}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })

    url = f"http://export.arxiv.org/api/query?{params}"
    with _urlopen(url, timeout=90) as resp:
        tree = ET.parse(resp)

    results = []
    for entry in tree.getroot().findall("atom:entry", NS):
        def text(tag, ns="atom"):
            el = entry.find(f"{ns}:{tag}", NS) if ns else entry.find(tag, NS)
            return el.text.strip() if el is not None and el.text else ""

        authors = [a.find("atom:name", NS).text for a in entry.findall("atom:author", NS)]
        categories_list = [c.get("term") for c in entry.findall("atom:category", NS)]
        primary = entry.find("arxiv:primary_category", NS)
        primary_cat = primary.get("term") if primary is not None else ""
        entry_id = text("id")
        m = re.search(r"abs/(.+?)(?:v\d+)?$", entry_id)
        arxiv_id = m.group(1) if m else ""

        if not arxiv_id:
            continue

        results.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(text("title").split()),
            "authors": authors,
            "abstract": " ".join(text("summary").split()),
            "published": text("published"),
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "categories": categories_list,
            "primary_category": primary_cat,
        })
    return results


def save_csv(papers: List[dict], output_path: str):
    """Save paper list to CSV."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fields = ["arxiv_id", "title", "authors", "primary_category", "url", "abstract"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for p in papers:
            row = dict(p)
            if isinstance(row.get("authors"), list):
                row["authors"] = "; ".join(row["authors"])
            writer.writerow(row)
    print(f"Saved {len(papers)} papers to {output_path}", file=sys.stderr)


# ── Mode 2: Detail (batch fetch alphaxiv overviews) ─────────────────────

def fetch_alphaxiv_batch(arxiv_ids: List[str]) -> dict:
    """Batch-fetch alphaxiv overviews for a list of arxiv IDs.
    Returns {arxiv_id: overview_text} dict."""
    results = {}
    for aid in arxiv_ids:
        url = f"https://alphaxiv.org/overview/{aid}.md"
        try:
            with _urlopen(url, timeout=30) as resp:
                text = resp.read().decode("utf-8", errors="replace")
                if text and len(text) > 100:
                    results[aid] = text
                else:
                    results[aid] = None
        except Exception:
            results[aid] = None
        time.sleep(0.5)  # rate limit
    return results


def cmd_list(args):
    cats = [c.strip() for c in args.categories.split(",")]
    output = args.output

    # Try HTML scraping first (faster, more reliable)
    papers = scrape_arxiv_listing(cats, args.days, args.max)

    # Fallback to API if scraping got nothing
    if not papers:
        print("HTML scraping returned no results, trying API...", file=sys.stderr)
        papers = fetch_via_api(cats, args.days, args.max)

    if output:
        save_csv(papers, output)
    else:
        json.dump(papers, sys.stdout, ensure_ascii=False, indent=2)
        print()

    print(f"Total: {len(papers)} papers", file=sys.stderr)


def cmd_detail(args):
    ids = [i.strip() for i in args.ids.split(",")]
    results = fetch_alphaxiv_batch(ids)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved details for {len(results)} papers to {args.output}", file=sys.stderr)
    else:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()


def main():
    parser = argparse.ArgumentParser(description="Fetch recent arxiv papers")
    sub = parser.add_subparsers(dest="mode")

    # list mode
    p_list = sub.add_parser("list", help="Fetch paper listing and save to CSV")
    p_list.add_argument("--categories", required=True, help="Comma-separated arxiv categories")
    p_list.add_argument("--days", type=int, default=2, help="How many days back to look")
    p_list.add_argument("--max", type=int, default=250, help="Max results per category")
    p_list.add_argument("--output", "-o", help="Output CSV path (default: stdout as JSON)")

    # detail mode
    p_detail = sub.add_parser("detail", help="Batch-fetch alphaxiv overviews for selected papers")
    p_detail.add_argument("--ids", required=True, help="Comma-separated arxiv IDs")
    p_detail.add_argument("--output", "-o", help="Output JSON path (default: stdout)")

    # Legacy: no subcommand → treat as list mode for backward compat
    parser.add_argument("--categories", help="(legacy) Comma-separated arxiv categories")
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--max", type=int, default=250)

    args = parser.parse_args()

    if args.mode == "list":
        cmd_list(args)
    elif args.mode == "detail":
        cmd_detail(args)
    elif args.categories:
        # Legacy mode: behave like old script
        cats = [c.strip() for c in args.categories.split(",")]
        papers = scrape_arxiv_listing(cats, args.days, args.max)
        if not papers:
            papers = fetch_via_api(cats, args.days, args.max)
        json.dump(papers, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
