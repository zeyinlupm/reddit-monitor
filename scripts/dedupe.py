#!/usr/bin/env python3
"""Canonicalize Reddit URLs and drop duplicate results from a CSV or JSON export.

A result is identified by (canonical post URL, comment id). Two comments on the
same post are two distinct results, not duplicates of each other.

    python dedupe.py candidates.csv clean.csv
    python dedupe.py --selfcheck
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# /r/<sub>/comments/<postid>[/<slug>[/<commentid>]] — the trailing id is present
# on comment permalinks, in both the /slug/<id> and /comment/<id> forms.
PERMALINK_RE = re.compile(
    r"/r/(?P<sub>[^/]+)/comments/(?P<post>[a-z0-9]+)"
    r"(?:/(?P<slug>[^/]*))?"
    r"(?:/(?P<comment>[a-z0-9]+))?",
    re.IGNORECASE,
)

URL_FIELD = "Canonical URL"
COMMENT_FIELD = "Comment ID"


def parse_permalink(value: str) -> tuple[str, str]:
    """Return (canonical post url, comment id). Falls back to the raw string."""
    raw = (value or "").strip()
    if not raw:
        return "", ""
    match = PERMALINK_RE.search(urlparse(raw).path)
    if not match:
        return raw, ""
    sub, post = match.group("sub"), match.group("post").lower()
    comment = (match.group("comment") or "").lower()
    return f"https://www.reddit.com/r/{sub}/comments/{post}/", comment


def dedupe(records: list[dict], url_field: str = URL_FIELD) -> tuple[list[dict], int]:
    """Drop repeat (url, comment id) pairs, keeping the first occurrence."""
    seen: set[tuple[str, str]] = set()
    kept: list[dict] = []
    for record in records:
        url, comment_from_url = parse_permalink(str(record.get(url_field, "")))
        # An explicit Comment ID column wins — the scraper reports it directly.
        comment = str(record.get(COMMENT_FIELD) or "").strip().lower() or comment_from_url
        record[url_field] = url
        record[COMMENT_FIELD] = comment
        key = (url, comment)
        if url and key in seen:
            continue
        if url:
            seen.add(key)
        kept.append(record)
    return kept, len(records) - len(kept)


def selfcheck() -> None:
    post = "https://www.reddit.com/r/londonontario/comments/abc123/"
    assert parse_permalink(post) == (post, "")
    # Comment permalinks resolve to the same post, with distinct comment ids.
    assert parse_permalink(f"{post}some_slug/def456/") == (post, "def456")
    assert parse_permalink(f"{post}comment/xyz789/?context=3") == (post, "xyz789")
    # Host and casing variants normalize to one canonical form.
    assert parse_permalink("http://old.reddit.com/r/londonontario/comments/ABC123")[0] == post
    assert parse_permalink("not a url") == ("not a url", "")
    assert parse_permalink("") == ("", "")

    rows = [
        {URL_FIELD: post, COMMENT_FIELD: ""},
        {URL_FIELD: post, COMMENT_FIELD: ""},                      # exact repeat
        {URL_FIELD: f"{post}slug/def456/", COMMENT_FIELD: ""},     # comment, id from url
        {URL_FIELD: f"{post}slug/ghi789/", COMMENT_FIELD: ""},     # different comment
        {URL_FIELD: post, COMMENT_FIELD: "def456"},                # same as row 3
    ]
    kept, removed = dedupe(rows)
    # Kept: the post, comment def456, comment ghi789.
    assert removed == 2, removed
    assert [(r[URL_FIELD], r[COMMENT_FIELD]) for r in kept] == [
        (post, ""),
        (post, "def456"),
        (post, "ghi789"),
    ], kept
    print("selfcheck ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--url-field", default=URL_FIELD)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()

    if args.selfcheck:
        selfcheck()
        return
    if not args.input or not args.output:
        parser.error("input and output are required unless --selfcheck is given")

    if args.input.suffix.lower() == ".json":
        records = json.loads(args.input.read_text(encoding="utf-8"))
        kept, removed = dedupe(records, args.url_field)
        args.output.write_text(json.dumps(kept, indent=2), encoding="utf-8")
    else:
        with args.input.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            records = list(reader)
            fieldnames = list(reader.fieldnames or [])
        for field in (args.url_field, COMMENT_FIELD):
            if field not in fieldnames:
                fieldnames.append(field)
        kept, removed = dedupe(records, args.url_field)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(kept)

    print(f"{len(kept)} kept, {removed} duplicates removed", file=sys.stderr)


if __name__ == "__main__":
    main()
