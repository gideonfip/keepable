#!/usr/bin/env python3
"""Import Field Theory X bookmarks into the Keepable Obsidian vault.

The important invariant is that Keepable `published` values are real Obsidian
dates in YYYY-MM-DD format. Field Theory's `postedAt` string is the canonical
source for X bookmark publish dates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


FIELD_THEORY_DB = Path.home() / ".ft-bookmarks" / "bookmarks.db"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=check)


def parse_fieldtheory_date(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    for fmt in (
        "%a %b %d %H:%M:%S +0000 %Y",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    match = re.match(r"^(\d{4}-\d{2}-\d{2})$", value)
    return match.group(1) if match else ""


def parse_cursor_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def yaml_string(value: str | None) -> str:
    return json.dumps(value or "", ensure_ascii=False)


def clean_spaces(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def excerpt(value: str | None, limit: int) -> str:
    text = clean_spaces(value)
    return text[:limit].rstrip()


def word_count(value: str | None) -> int:
    return len(re.findall(r"\b\S+\b", value or ""))


def safe_filename(title: str, fallback: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|#^\[\]]+", "", title)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    if not name:
        name = fallback
    return name[:140].rstrip() + ".md"


def find_existing_note(vault: Path, url: str) -> Path | None:
    result = run(["rg", "-l", "--fixed-strings", url, str(vault), "--glob", "*.md"], check=False)
    paths = [line for line in result.stdout.splitlines() if line.strip()]
    return Path(paths[0]) if paths else None


def get_published_value(path: Path) -> str | None:
    match = re.search(r"^published:[ \t]*([^\n]*)$", path.read_text(errors="replace"), re.M)
    return match.group(1).strip() if match else None


def normalize_existing_published(path: Path, published: str) -> bool:
    if not published:
        return False
    text = path.read_text(errors="replace")
    current = get_published_value(path)
    if current == published:
        return False
    if current is None:
        new_text = re.sub(r"^(source:\s*.*)$", rf"\1\npublished: {published}", text, count=1, flags=re.M)
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", current):
        return False
    else:
        new_text = re.sub(r"^published:[ \t]*[^\n]*$", f"published: {published}", text, count=1, flags=re.M)
    if new_text != text:
        path.write_text(new_text)
        return True
    return False


def create_author_page(vault: Path, handle: str, *, dry_run: bool) -> None:
    if not handle:
        return
    authors_dir = vault / "Author"
    authors_dir.mkdir(parents=True, exist_ok=True)
    path = authors_dir / f"{handle}.md"
    if path.exists() or dry_run:
        return
    content = f'''---
aliases:
  - {handle}
---

# {handle}

## Content

```dataview
TABLE
  file.folder AS "Category",
  published AS "Published",
  description AS "Description"
FROM "2 - Source Materials"
WHERE contains(author, "{handle}")
SORT published DESC
```
'''
    path.write_text(content)


def destination_for(vault: Path, item: dict[str, Any], body: str) -> Path:
    source_root = vault / "2 - Source Materials"
    if item.get("articleText") or word_count(body) >= 300:
        return source_root / "X Articles"
    return source_root / "X Tweets"


def build_note(vault: Path, item: dict[str, Any], published: str) -> tuple[Path, str]:
    handle = (item.get("authorHandle") or item.get("authorName") or "").strip().lstrip("@")
    body = (item.get("articleText") or item.get("text") or "").strip()
    title_source = item.get("articleTitle") or excerpt(body, 120) or f"Post by @{handle} on X"
    title = excerpt(title_source, 140)
    description = excerpt(body, 240) or title
    folder = destination_for(vault, item, body)
    folder.mkdir(parents=True, exist_ok=True)
    fallback = item.get("tweetId") or item.get("id") or "x-bookmark"
    path = folder / safe_filename(title, fallback)
    if path.exists() and (item.get("url") or "") not in path.read_text(errors="replace"):
        path = folder / safe_filename(f"{title} {fallback}", fallback)

    links = item.get("links") or []
    if links:
        body += "\n\n## Links\n\n" + "\n".join(f"- {link}" for link in links)
    if not body:
        body = title

    author_line = f'  - "[[{handle}]]"' if handle else ""
    created = date.today().isoformat()
    published_line = f"published: {published}" if published else "published:"
    note = f'''---
title: {yaml_string(title)}
source: {yaml_string(item.get("url"))}
author:
{author_line}
{published_line}
created: {created}
description: {yaml_string(description)}
site: "X (Twitter)"
domain: "x.com"
language: {yaml_string(item.get("language") or "en")}
wordCount: {word_count(body)}
favicon: "//abs.twimg.com/favicons/twitter.ico"
---

{body}
'''
    return path, note


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def bookmark_cursor(row: dict[str, Any]) -> str:
    return row.get("bookmarkedAt") or row.get("syncedAt") or ""


def db_row_to_item(row: sqlite3.Row) -> dict[str, Any]:
    def json_list(value: str | None) -> list[Any]:
        if not value:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []

    return {
        "id": row["id"],
        "tweetId": row["tweet_id"],
        "url": row["url"],
        "text": row["text"],
        "authorHandle": row["author_handle"],
        "authorName": row["author_name"],
        "postedAt": row["posted_at"],
        "bookmarkedAt": row["bookmarked_at"],
        "syncedAt": row["synced_at"],
        "language": row["language"],
        "links": json_list(row["links_json"]),
        "articleTitle": row["article_title"],
        "articleText": row["article_text"],
        "articleSite": row["article_site"],
    }


def max_db_cursor() -> str:
    if not FIELD_THEORY_DB.exists():
        return ""
    conn = sqlite3.connect(FIELD_THEORY_DB)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT MAX(COALESCE(NULLIF(bookmarked_at, ''), synced_at)) AS cursor
            FROM bookmarks
            WHERE COALESCE(NULLIF(bookmarked_at, ''), synced_at) IS NOT NULL
            """
        ).fetchone()
        return row["cursor"] or ""
    finally:
        conn.close()


def load_items_since_last_sync(state_file: Path, batch_size: int, *, dry_run: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    state = load_state(state_file)
    last_cursor = state.get("last_cursor")
    if not last_cursor:
        cursor = max_db_cursor()
        state.update(
            {
                "last_cursor": cursor,
                "last_run_at": datetime.now(timezone.utc).isoformat(),
                "last_mode": "initialized",
                "note": "Initialized cursor from current Field Theory database; future runs import only newer bookmark/sync entries.",
            }
        )
        if not dry_run:
            save_state(state_file, state)
        return [], state

    items: list[dict[str, Any]] = []
    cursor = last_cursor
    seen_urls: set[str] = set()
    conn = sqlite3.connect(FIELD_THEORY_DB)
    conn.row_factory = sqlite3.Row
    try:
        while True:
            rows = conn.execute(
                """
                SELECT *
                FROM bookmarks
                WHERE COALESCE(NULLIF(bookmarked_at, ''), synced_at) > ?
                ORDER BY COALESCE(NULLIF(bookmarked_at, ''), synced_at) ASC
                LIMIT ?
                """,
                (cursor, batch_size),
            ).fetchall()
            if not rows:
                break
            for row in rows:
                item = db_row_to_item(row)
                url = item.get("url") or ""
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    items.append(item)
            latest = max(bookmark_cursor(db_row_to_item(row)) for row in rows)
            if latest <= cursor:
                break
            cursor = latest
            if len(rows) < batch_size:
                break
        return items, state
    finally:
        conn.close()


def load_items(after: str | None, before: str | None, limit: int) -> list[dict[str, Any]]:
    command = ["ft", "list", "--json", "--limit", str(limit)]
    if after:
        command += ["--after", after]
    if before:
        command += ["--before", before]
    result = run(command)
    return json.loads(result.stdout)


def update_cursor_state(
    state_file: Path,
    state: dict[str, Any],
    items: list[dict[str, Any]],
    *,
    dry_run: bool,
    created: int,
    skipped: int,
    normalized: int,
    invalid_dates: int,
) -> None:
    cursors = [bookmark_cursor(item) for item in items if bookmark_cursor(item)]
    if cursors:
        latest_cursor = max(cursors)
        latest_item = max(items, key=bookmark_cursor)
        state["last_cursor"] = latest_cursor
        state["last_url"] = latest_item.get("url")
        state["last_bookmarked_at"] = latest_item.get("bookmarkedAt")
        state["last_synced_at"] = latest_item.get("syncedAt")
    state.update(
        {
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "last_mode": "since-last-sync",
            "last_counts": {
                "considered": len(items),
                "created": created,
                "skipped_existing": skipped,
                "normalized_existing_dates": normalized,
                "invalid_or_missing_dates": invalid_dates,
            },
        }
    )
    if not dry_run:
        save_state(state_file, state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Field Theory bookmarks into Keepable")
    parser.add_argument("--vault", type=Path, required=True, help="Path to the Keepable Obsidian vault")
    parser.add_argument("--after", help="Only import bookmarks posted after YYYY-MM-DD")
    parser.add_argument("--before", help="Only import bookmarks posted before YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=100, help="Manual ft list limit, or since-last-sync batch size")
    parser.add_argument("--since-last-sync", action="store_true", help="Only import bookmarks newer than the saved Field Theory cursor")
    parser.add_argument("--state-file", type=Path, help="Cursor state file path (default: <vault>/.agents/keepable-x-bookmark-import-state.json)")
    parser.add_argument("--sync", action="store_true", help="Run ft sync before importing")
    parser.add_argument("--rebuild", action="store_true", help="Use ft sync --rebuild")
    parser.add_argument("--browser", help="Browser to read X session from, e.g. chrome or brave")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing notes")
    args = parser.parse_args()

    vault = args.vault.expanduser().resolve()
    if not vault.exists():
        sys.stderr.write(f"Vault path does not exist: {vault}\n")
        return 1

    state_file = args.state_file or (vault / ".agents" / "keepable-x-bookmark-import-state.json")

    if args.sync:
        sync_cmd = ["ft", "sync", "--yes", "--no-media"]
        if args.browser:
            sync_cmd += ["--browser", args.browser]
        if args.rebuild:
            sync_cmd.append("--rebuild")
        print("Running:", " ".join(sync_cmd))
        sync = run(sync_cmd, check=False)
        if sync.returncode != 0:
            sys.stderr.write(sync.stdout)
            sys.stderr.write(sync.stderr)
            return sync.returncode

    state: dict[str, Any] = {}
    initialized_cursor = False
    if args.since_last_sync:
        items, state = load_items_since_last_sync(state_file, args.limit, dry_run=args.dry_run)
        initialized_cursor = state.get("last_mode") == "initialized" and not items
    else:
        items = load_items(args.after, args.before, args.limit)
    created: list[Path] = []
    skipped: list[Path] = []
    normalized: list[Path] = []
    invalid_dates: list[str] = []

    for item in items:
        url = item.get("url") or ""
        if not url:
            continue
        published = parse_fieldtheory_date(item.get("postedAt"))
        if not published:
            invalid_dates.append(url)

        existing = find_existing_note(vault, url)
        if existing:
            if normalize_existing_published(existing, published):
                normalized.append(existing)
            skipped.append(existing)
            continue

        path, note = build_note(vault, item, published)
        handle = (item.get("authorHandle") or item.get("authorName") or "").strip().lstrip("@")
        if not args.dry_run:
            path.write_text(note)
            create_author_page(vault, handle, dry_run=False)
        created.append(path)

    print(f"Considered: {len(items)}")
    print(f"Created: {len(created)}")
    for path in created:
        print("  created", path.relative_to(vault))
    print(f"Skipped existing: {len(skipped)}")
    print(f"Normalized existing dates: {len(normalized)}")
    for path in normalized:
        print("  normalized", path.relative_to(vault))
    print(f"Invalid or missing Field Theory dates: {len(invalid_dates)}")
    for url in invalid_dates:
        print("  invalid-date", url)

    if args.since_last_sync:
        update_cursor_state(
            state_file,
            state,
            items,
            dry_run=args.dry_run,
            created=len(created),
            skipped=len(skipped),
            normalized=len(normalized),
            invalid_dates=len(invalid_dates),
        )
        print(f"State file: {state_file}")
        if initialized_cursor:
            print("Initialized last-sync cursor; no historical bookmarks imported in this lightweight run.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
