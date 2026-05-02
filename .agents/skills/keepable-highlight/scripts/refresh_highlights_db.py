#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n([\s\S]*?)\n---\n?", re.M)
FIELD_RE = re.compile(r"^(title|author|published):\s*(.*)$", re.M)
HIGHLIGHT_RE = re.compile(r"(?<!\w)(={2,})([\s\S]*?)\1(?!\w)")


def normalize_author(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""

    # Handle list-like scalar forms: - "[[Name]]"
    if value.startswith("- "):
        value = value[2:].strip()

    # Unwrap nested quotes if present
    for _ in range(3):
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1].strip()

    # Normalize escaped quotes and repeated spacing
    value = value.replace('\\"', '"')
    value = re.sub(r"\s+", " ", value).strip()

    # If a wikilink exists, keep the first wikilink as author
    wikilink = re.search(r"\[\[[^\]]+\]\]", value)
    if wikilink:
        return wikilink.group(0)

    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    fm_text = match.group(1)
    body = text[match.end():]
    data: dict[str, str] = {}
    for key, value in FIELD_RE.findall(fm_text):
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        data[key] = value

    # Parse multiline author lists:
    # author:
    #   - "[[Name]]"
    if not data.get("author"):
        author_block = re.search(
            r"^author:\s*\n((?:\s{2,}-.*(?:\n|$))+)",
            fm_text,
            re.M,
        )
        if author_block:
            for line in author_block.group(1).splitlines():
                line = re.sub(r"^\s*-\s*", "", line).strip()
                line = normalize_author(line)
                if line:
                    data["author"] = line
                    break

    if data.get("author"):
        data["author"] = normalize_author(data["author"])

    return data, body


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def safe_filename_part(value: str, limit: int = 80) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        value = "untitled"
    return value[:limit]


def build_base_content() -> str:
    return """filters:
  and:
    - file.inFolder("2 - Source Materials/Highlights DB")
    - file.ext == "md"
formulas:
  name_link: 'if(source_note, link(source_note, name), name)'
  published_date: 'if(source_note, file(source_note).properties.published, date)'
properties:
  highlight:
    displayName: Highlight
  formula.name_link:
    displayName: Name
  author:
    displayName: Author
  formula.published_date:
    displayName: Date
views:
  - type: table
    name: All Highlights
    order:
      - highlight
      - formula.name_link
      - author
      - formula.published_date
    sort:
      - property: formula.published_date
        direction: DESC
    columnSize:
      highlight: 700
      formula.name_link: 320
      author: 180
      formula.published_date: 120
"""


EXCLUDED_FOLDERS = {"Highlights DB", "Emails"}
EXCLUDED_FILES = {"Highlights View.md", "Highlights.md"}


def source_files(source_root: Path) -> list[Path]:
    files: list[Path] = []
    for md_file in source_root.rglob("*.md"):
        if any(f in md_file.parts for f in EXCLUDED_FOLDERS):
            continue
        if md_file.name in EXCLUDED_FILES:
            continue
        files.append(md_file)
    return files


CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")

def strip_code_blocks(text: str) -> str:
    text = CODE_FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def extract_entries(vault_root: Path, source_file: Path) -> list[dict[str, str]]:
    text = source_file.read_text(encoding="utf-8", errors="ignore")
    fm, body = parse_frontmatter(text)
    body = strip_code_blocks(body)

    article = fm.get("title", source_file.stem).strip()
    author = fm.get("author", "").strip()
    published = fm.get("published", "").strip()
    rel_source = source_file.relative_to(vault_root).as_posix()

    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    idx = 1
    for match in HIGHLIGHT_RE.finditer(body):
        raw = match.group(2)
        highlight = re.sub(r"\s+", " ", raw).strip()
        if len(highlight) < 8:
            continue
        if highlight in seen:
            continue
        seen.add(highlight)
        entries.append(
            {
                "idx": str(idx),
                "name": f"{article} #{idx}",
                "highlight": highlight,
                "author": author,
                "date": published,
                "source_note": rel_source,
                "source_stem": source_file.stem,
            }
        )
        idx += 1
    return entries


def build_record_content(entry: dict[str, str]) -> str:
    return "\n".join(
        [
            "---",
            f"name: {yaml_quote(entry['name'])}",
            f"highlight: {yaml_quote(entry['highlight'])}",
            f"author: {yaml_quote(entry['author'])}",
            f"date: {yaml_quote(entry['date'])}",
            f"source_note: {yaml_quote(entry['source_note'])}",
            'type: "highlight"',
            "---",
            "",
            entry["highlight"],
            "",
        ]
    )


def parse_generated_record(path: Path) -> tuple[str, int] | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    fm_text = fm_match.group(1)
    src_match = re.search(r'^source_note:\s*"([^"]*)"$', fm_text, re.M)
    name_match = re.search(r'^name:\s*"([^"]*)"$', fm_text, re.M)
    if not src_match or not name_match:
        return None
    src = src_match.group(1)
    name = name_match.group(1)
    idx_match = re.search(r"#(\d+)$", name)
    if not idx_match:
        return None
    return src, int(idx_match.group(1))


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {"version": 1, "sources": {}}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"version": 1, "sources": {}}
        data.setdefault("version", 1)
        data.setdefault("sources", {})
        return data
    except Exception:
        return {"version": 1, "sources": {}}


def save_state(state_file: Path, source_hashes: dict[str, str]) -> None:
    payload = {
        "version": 1,
        "sources": {k: {"hash": v} for k, v in sorted(source_hashes.items())},
    }
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def run(vault_root: Path, dry_run: bool, full_rebuild: bool) -> tuple[int, int, int, int]:
    source_root = vault_root / "2 - Source Materials"
    out_dir = source_root / "Highlights DB"
    base_file = vault_root / "0 - Reading" / "🖊️ Highlights Database.base"
    state_file = vault_root / ".agents" / "skills" / "keepable-highlight" / "state.json"

    if not source_root.exists():
        raise FileNotFoundError(f"Missing source folder: {source_root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    files = source_files(source_root)
    source_count = len(files)

    # Hash current source files
    source_hashes: dict[str, str] = {}
    path_by_rel: dict[str, Path] = {}
    for md_file in files:
        rel_source = md_file.relative_to(vault_root).as_posix()
        raw = md_file.read_bytes()
        source_hashes[rel_source] = hashlib.sha1(raw).hexdigest()
        path_by_rel[rel_source] = md_file

    state = load_state(state_file)
    previous_hashes = {
        k: v.get("hash", "")
        for k, v in state.get("sources", {}).items()
        if isinstance(v, dict)
    }

    changed_sources = set()
    removed_sources = set()
    if full_rebuild or not previous_hashes:
        changed_sources = set(source_hashes.keys())
        removed_sources = set()
    else:
        for rel, h in source_hashes.items():
            if previous_hashes.get(rel) != h:
                changed_sources.add(rel)
        removed_sources = set(previous_hashes.keys()) - set(source_hashes.keys())

    # Index existing generated records
    existing_index: dict[str, dict[int, Path]] = {}
    for p in out_dir.glob("*.md"):
        parsed = parse_generated_record(p)
        if not parsed:
            continue
        src, idx = parsed
        existing_index.setdefault(src, {})[idx] = p

    highlights_total = 0
    records_written = 0
    records_deleted = 0

    if full_rebuild and not dry_run:
        for p in out_dir.glob("*.md"):
            p.unlink()
            records_deleted += 1
        existing_index = {}

    # Remove records for deleted sources
    for rel_source in removed_sources:
        for p in existing_index.get(rel_source, {}).values():
            if not dry_run and p.exists():
                p.unlink()
            records_deleted += 1

    # Compute total highlight count across all source files
    # Parse unchanged files only for count in dry-run/reporting accuracy.
    for rel_source, source_path in path_by_rel.items():
        entries = extract_entries(vault_root, source_path)
        highlights_total += len(entries)

        existing_for_source = existing_index.get(rel_source, {})
        new_indices = set(range(1, len(entries) + 1))

        # Always delete stale entries (indices no longer present in current file)
        stale_indices = set(existing_for_source.keys()) - new_indices
        for idx in stale_indices:
            p = existing_for_source[idx]
            if not dry_run and p.exists():
                p.unlink()
            records_deleted += 1

        if rel_source not in changed_sources:
            continue

        # Upsert changed entries
        for idx, entry in enumerate(entries, start=1):
            if dry_run:
                continue
            target = existing_for_source.get(idx)
            if target is None:
                file_stub = safe_filename_part(entry["source_stem"])
                source_hash_short = source_hashes[rel_source][:8]
                note_name = f"{file_stub} - {source_hash_short} - {idx}.md"
                target = out_dir / note_name
            target.write_text(build_record_content(entry), encoding="utf-8")
            records_written += 1

    if not dry_run:
        base_file.parent.mkdir(parents=True, exist_ok=True)
        base_file.write_text(build_base_content(), encoding="utf-8")
        save_state(state_file, source_hashes)

    return source_count, highlights_total, records_written, records_deleted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild Obsidian Highlights DB from ==...== markers."
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Vault root path (default: inferred from skill location).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and count highlights without writing files.",
    )
    parser.add_argument(
        "--full-rebuild",
        action="store_true",
        help="Force full rebuild instead of incremental sync.",
    )
    args = parser.parse_args()

    source_count, highlight_count, records_written, records_deleted = run(
        args.vault.expanduser().resolve(),
        args.dry_run,
        args.full_rebuild,
    )

    mode = "DRY RUN" if args.dry_run else "UPDATED"
    sync_mode = "full rebuild" if args.full_rebuild else "incremental sync"
    print(f"[{mode}] Mode: {sync_mode}")
    print(f"[{mode}] Scanned source notes: {source_count}")
    print(f"[{mode}] Highlights found: {highlight_count}")
    if not args.dry_run:
        print(f"[UPDATED] Records upserted: {records_written}")
        print(f"[UPDATED] Records deleted: {records_deleted}")
        print("[UPDATED] Synced: 2 - Source Materials/Highlights DB")
        print("[UPDATED] Wrote: 0 - Reading/Highlights Database.base")


if __name__ == "__main__":
    main()
