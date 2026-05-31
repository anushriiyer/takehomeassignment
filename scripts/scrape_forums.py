#!/usr/bin/env python3
"""Scrape LangChain forum threads and save one JSON file per link to data/forums/."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "forum_links.txt"
FORUMS_DIR = ROOT / "data" / "forums"

FORUMS_DIR.mkdir(parents=True, exist_ok=True)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def url_to_json_endpoint(url: str) -> str:
    url = url.rstrip("/")
    if url.endswith(".json"):
        return url
    return f"{url}.json"


def extract_topic_id(url: str) -> str:
    match = re.search(r"/(\d+)/?$", url.rstrip("/"))
    return match.group(1) if match else "unknown"


def normalize_tags(raw: dict) -> list[str]:
    tags = raw.get("tags", [])
    if not tags:
        return []
    if isinstance(tags[0], str):
        return tags
    return [tag["name"] for tag in tags if isinstance(tag, dict) and "name" in tag]


def load_urls(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def scrape_forum(url: str) -> dict:
    json_url = url_to_json_endpoint(url)
    print(f"Downloading {json_url}")

    response = requests.get(json_url, timeout=30)
    response.raise_for_status()
    raw = response.json()

    topic_id = str(raw["id"])
    tags = normalize_tags(raw)

    posts = []
    for post in raw["post_stream"]["posts"]:
        posts.append(
            {
                "post_number": post["post_number"],
                "author": post["username"],
                "role": post.get("user_title") or "user",
                "created_at": post["created_at"],
                "body": clean_html(post["cooked"]),
            }
        )

    # Shape matches src/chunkers.py chunk_forum() expectations
    return {
        "id": f"forum_{topic_id}",
        "source_type": "forum",
        "title": raw["title"],
        "url": url,
        "date": raw.get("created_at", posts[0]["created_at"] if posts else ""),
        "created_at": raw.get("created_at", ""),
        "last_posted_at": raw.get("last_posted_at", ""),
        "tags": tags,
        "views": raw.get("views", 0),
        "posts": posts,
    }


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_FILE
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else FORUMS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    urls = load_urls(input_path)
    if not urls:
        print(f"No URLs found in {input_path}")
        sys.exit(1)

    print(f"Scraping {len(urls)} forum threads → {output_dir}\n")

    succeeded = 0
    failed = 0

    for url in urls:
        try:
            doc = scrape_forum(url)
            topic_id = extract_topic_id(url)
            output_path = output_dir / f"forum_{topic_id}.json"

            output_path.write_text(
                json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Saved {output_path}\n")
            succeeded += 1
        except Exception as exc:
            print(f"Failed: {url}")
            print(f"  {exc}\n")
            failed += 1

    print(f"Done. {succeeded} saved, {failed} failed.")


if __name__ == "__main__":
    main()
