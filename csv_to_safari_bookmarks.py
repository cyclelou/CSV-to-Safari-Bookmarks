#!/usr/bin/env python3
"""Convert URL CSV files into Safari-importable bookmarks HTML."""

from __future__ import annotations

import argparse
import csv
import html
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class Counters:
    rows_read: int = 0
    written: int = 0
    duplicates: int = 0
    invalid: int = 0


def _read_csv_candidates(path: str) -> tuple[list[str], int]:
    """Return first non-empty cell per row and total rows read."""
    candidates: list[str] = []
    rows_read = 0

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows_read += 1
            first_non_empty = ""
            for cell in row:
                value = cell.strip()
                if value:
                    first_non_empty = value
                    break
            if first_non_empty:
                candidates.append(first_non_empty)

    return candidates, rows_read


def extract_urls_from_csv(path: str) -> list[str]:
    """Extract first non-empty cell from each CSV row, skipping blank rows."""
    candidates, _rows_read = _read_csv_candidates(path)
    return candidates


def is_valid_url(url: str, allow_non_http: bool = False) -> bool:
    """Validate a URL for bookmark import."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False

    if allow_non_http:
        return True

    return parsed.scheme.lower() in {"http", "https"}


def dedupe_preserve_order(urls: list[str]) -> list[str]:
    """Remove duplicates while preserving input order."""
    seen: set[str] = set()
    out: list[str] = []

    for url in urls:
        if url not in seen:
            seen.add(url)
            out.append(url)

    return out


def build_bookmark_html(urls: list[str], folder_name: str) -> str:
    """Build Safari-compatible Netscape bookmarks HTML."""
    escaped_folder = html.escape(folder_name, quote=True)

    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">",
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
        f"    <DT><H3>{escaped_folder}</H3>",
        "    <DL><p>",
    ]

    for url in urls:
        escaped_url = html.escape(url, quote=True)
        lines.append(f"        <DT><A HREF=\"{escaped_url}\">{escaped_url}</A>")

    lines.extend([
        "    </DL><p>",
        "</DL><p>",
        "",
    ])

    return "\n".join(lines)


def convert_csv_to_bookmarks(
    input_path: str,
    output_path: str,
    folder_name: str | None = None,
    allow_non_http: bool = False,
) -> Counters:
    """Convert URL CSV into bookmarks HTML and write to output_path."""
    counters = Counters()

    candidates, counters.rows_read = _read_csv_candidates(input_path)

    valid_urls: list[str] = []
    for candidate in candidates:
        if is_valid_url(candidate, allow_non_http=allow_non_http):
            valid_urls.append(candidate)
        else:
            counters.invalid += 1

    deduped_urls = dedupe_preserve_order(valid_urls)
    counters.duplicates = len(valid_urls) - len(deduped_urls)
    counters.written = len(deduped_urls)

    if counters.written == 0:
        raise ValueError("No valid URLs found in input CSV.")

    if folder_name is None:
        folder_name = Path(input_path).stem or "Imported"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    html_doc = build_bookmark_html(deduped_urls, folder_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    return counters


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a CSV list of URLs into Safari-importable bookmarks HTML."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output HTML file")
    parser.add_argument(
        "--folder",
        default=None,
        help="Optional folder name inside bookmarks HTML (defaults to input filename stem)",
    )
    parser.add_argument(
        "--allow-non-http",
        action="store_true",
        help="Allow non-http(s) URLs as long as scheme and host are present",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        counters = convert_csv_to_bookmarks(
            input_path=args.input,
            output_path=args.output,
            folder_name=args.folder,
            allow_non_http=args.allow_non_http,
        )
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error: Could not read input file '{args.input}': {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"rows_read={counters.rows_read}")
    print(f"valid_urls_written={counters.written}")
    print(f"duplicates_skipped={counters.duplicates}")
    print(f"invalid_skipped={counters.invalid}")
    print(f"output={args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
