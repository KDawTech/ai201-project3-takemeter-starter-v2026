#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class StripHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        return " ".join(" ".join(self.parts).split())


def clean_html(value: str) -> str:
    parser = StripHTML()
    parser.feed(value or "")
    text = html.unescape(parser.text())
    return re.sub(r"\s+", " ", text).strip()


def fetch_page(tag: str, page: int, page_size: int = 100) -> dict:
    params = {
        "site": "stackoverflow",
        "tagged": tag,
        "sort": "creation",
        "order": "desc",
        "pagesize": min(page_size, 100),
        "page": page,
        "filter": "withbody",
    }
    url = "https://api.stackexchange.com/2.3/questions?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TakeMeter-AI201/1.0 student coursework"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="python")
    ap.add_argument("--count", type=int, default=220)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    raw_path = root / "raw_posts.csv"
    labels_path = root / "labels.csv"

    if not args.force and (raw_path.exists() or labels_path.exists()):
        raise SystemExit(
            "raw_posts.csv or labels.csv already exists. "
            "Rename/delete it first, or rerun with --force."
        )

    rows = []
    seen = set()
    page = 1

    print(f"Collecting {args.count} public Stack Overflow questions tagged [{args.tag}] ...")

    while len(rows) < args.count:
        payload = fetch_page(args.tag, page)

        for item in payload.get("items", []):
            qid = str(item.get("question_id", ""))
            if not qid or qid in seen:
                continue

            title = clean_html(item.get("title", ""))
            body = clean_html(item.get("body", ""))
            text = f"{title}\n\n{body}".strip()
            if len(text) < 80:
                continue

            seen.add(qid)
            rows.append(
                {
                    "id": qid,
                    "title": title,
                    "text": text,
                    "url": item.get("link", ""),
                    "score": item.get("score", 0),
                    "created_utc": item.get("creation_date", ""),
                }
            )
            if len(rows) >= args.count:
                break

        print(f"  collected {len(rows)}")

        if payload.get("backoff"):
            time.sleep(int(payload["backoff"]) + 1)
        if not payload.get("has_more"):
            break

        page += 1
        time.sleep(0.25)

    if len(rows) < 150:
        raise SystemExit(
            f"Only collected {len(rows)} usable questions. "
            "Try another tag such as javascript, java, or reactjs."
        )

    with raw_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "title", "text", "url", "score", "created_utc"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with labels_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "note"])
        writer.writeheader()
        for i, row in enumerate(rows):
            writer.writerow(
                {
                    "text": row["text"],
                    "label": "",
                    "note": "cold" if i < 20 else "to_label",
                }
            )

    print(f"Wrote {raw_path.name}: {len(rows)} posts")
    print(f"Wrote {labels_path.name}: {len(rows)} rows")
    print("IMPORTANT: label rows 1-20 manually with no AI help.")


if __name__ == "__main__":
    main()
