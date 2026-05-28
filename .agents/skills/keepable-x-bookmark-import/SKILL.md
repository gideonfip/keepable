---
name: keepable-x-bookmark-import
description: "Import the latest X/Twitter bookmarks from Field Theory (`ft`) into the Keepable Obsidian vault. Use this skill whenever the user wants to sync recent browser/X bookmarks, import Field Theory bookmarks into Obsidian, refresh Keepable from `~/.ft-bookmarks`, or troubleshoot bookmark dates in Keepable. This skill is especially important when `published` dates must be parsed correctly as `YYYY-MM-DD`."
user-invokable: true
disable-model-invocation: false
---

# X Bookmark to Keepable Import

Sync the local Field Theory bookmark store, collect the latest bookmark URLs, and import missing bookmarks into the Keepable vault using the same destination/frontmatter conventions as `keepable-clip`.

## First Run Setup

On first use, the agent must ask the user three questions:

1. **Vault path**: Where is the Keepable vault located?
2. **Browser**: Which browser does Field Theory use to authenticate with X? (e.g. `chrome`, `brave`, `firefox`)
3. **Import mode**: Use lightweight cursor mode (`--since-last-sync`) for ongoing sync, or manual window (`--after YYYY-MM-DD`) for backfill.

Store the vault path and browser preference for subsequent runs.

## What This Skill Does

1. Runs Field Theory (`ft`) so the local bookmark database reflects the browser/X bookmark state.
2. Filters the latest bookmarks through either a lightweight saved cursor or Field Theory CLI (`ft list --json`).
3. Uses each bookmark URL as the source of truth for duplicate detection.
4. Imports missing X bookmarks into `2 - Source Materials/X Tweets/` or `2 - Source Materials/X Articles/` using Keepable clipping conventions.
5. Parses Field Theory `postedAt` values into strict Obsidian date properties: `published: YYYY-MM-DD`.
6. Verifies every imported or existing matching note has a valid `published` date.

## Required Paths

- Keepable vault: asked on first use
- Field Theory data: `~/.ft-bookmarks/bookmarks.db`
- Field Theory CLI: `ft`
- Keepable clip skill reference: `.agents/skills/keepable-clip/SKILL.md` (relative to vault)

## Standard Workflow

For routine imports, use the lightweight cursor mode. It records the last Field Theory bookmark/sync timestamp processed and only imports newer entries next time:

```bash
python3 .agents/skills/keepable-x-bookmark-import/scripts/import_fieldtheory_to_keepable.py --vault "<vault-path>" --sync --browser <browser> --since-last-sync
```

The cursor is stored in:

```text
<vault-path>/.agents/keepable-x-bookmark-import-state.json
```

On the first `--since-last-sync` run, the script initializes the cursor from the current Field Theory database and imports no history. This is intentional: it avoids reprocessing the whole bookmark archive after the vault has already been bootstrapped.

In `--since-last-sync` mode, `--limit` is a batch size, not a hard total cap. The script loops until there are no newer Field Theory rows left, so 21, 100, or more new bookmarks will all be considered across batches. The default batch size is `100`.

For a manual backfill window, run the bundled importer script with `--after`:

```bash
python3 .agents/skills/keepable-x-bookmark-import/scripts/import_fieldtheory_to_keepable.py --vault "<vault-path>" --sync --browser <browser> --after 2026-01-01
```

Use `--after YYYY-MM-DD` to control the import window. If the user asks for the latest bookmarks and gives no date, use a recent window such as `--after 2026-01-01` or the date implied by their request.

For a dry run:

```bash
python3 .agents/skills/keepable-x-bookmark-import/scripts/import_fieldtheory_to_keepable.py --vault "<vault-path>" --sync --browser <browser> --after 2026-01-01 --dry-run
```

## Field Theory Sync Rules

Prefer this sync command because it updates the browser-sourced bookmark entries without doing a slow full rebuild or folder sync:

```bash
ft sync --yes --no-media
```

If the user explicitly wants a full refresh, add `--rebuild`:

```bash
ft sync --yes --no-media --rebuild
```

If auth fails with the chosen browser, retry with a different browser from `chrome`, `brave`, `firefox`, `edge`.

If sync fails because browser auth is unavailable, stop and report the sync error. Do not fabricate bookmarks.

## Date Rules

There are two separate dates:

- `postedAt`: when the X post was published. Use this for the note's `published` property.
- `bookmarkedAt`/`syncedAt`: when Field Theory saw the bookmark. Use this only for the lightweight import cursor.

Field Theory stores X dates as strings like:

```text
Mon Apr 27 13:05:26 +0000 2026
```

Always parse this with:

```python
datetime.strptime(posted_at, "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d")
```

Never use `posted_at[:10]`; that creates invalid values like `Mon Apr 27`.

For deciding what to import in `--since-last-sync` mode, prefer `bookmarkedAt` when Field Theory has it. If Field Theory does not have a reliable bookmark timestamp, use `syncedAt` as the cursor. Do not use `postedAt` for the cursor because old posts can be newly bookmarked.

Valid Keepable frontmatter must contain:

```yaml
published: YYYY-MM-DD
created: YYYY-MM-DD
```

If `postedAt` is missing or unparseable, leave `published:` empty and report that URL as requiring manual review. Do not put `null`, a full ISO datetime, or a natural-language date in `published`.

## Import Rules

- Check duplicates by searching the vault for the exact `source` URL before creating a note.
- Skip existing notes unless their `published` field is malformed; then normalize the date if Field Theory has a valid `postedAt` for that URL.
- Use the Field Theory URL as `source`.
- Use author wikilinks as a YAML array: `author:\n  - "[[handle]]"`.
- Create missing author pages in `Author/` using the existing Dataview format.
- Put short X posts in `X Tweets/`.
- Put long X article/thread content in `X Articles/` only when the text is long-form, usually `>= 300` words or Field Theory has `articleText`.
- Preserve full text from Field Theory; do not truncate the note body.
- Include links from Field Theory under a `## Links` section when present.

## Verification

After import, the script prints:

- number of Field Theory bookmarks considered
- notes created
- existing notes skipped
- existing notes date-normalized
- missing or invalid dates

Report these counts to the user. If invalid dates remain, list the affected URLs/files.

## Relationship To `keepable-clip`

This skill automates the batch intake queue around `keepable-clip`. It follows the Keepable clip frontmatter/destination conventions, but uses Field Theory as the extractor for X bookmarks because Field Theory already has the canonical X URL, author, text, and posted timestamp. This avoids the known failure mode where X dates are clipped as `Mon Apr 27` or full datetimes instead of `YYYY-MM-DD`.
