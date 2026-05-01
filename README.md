
# Keepable

An Obsidian vault for people who want to bookmark and highlight a wide variety of sources.

Keepable runs locally on your device and serves as a free read-later app built completely on Obsidian, with a suite of Agent Skills that automate the tedious parts of maintaining the database.

Clip articles, tweets, YouTube videos, Reddit posts, and more. Then query, filter, and surface them with [Obsidian Bases](https://obsidian.md/bases), while highlighting in Reader View.

Used together with the [Obsidian Web Clipper](https://obsidian.md/clipper) and my [Clipper Templates](https://github.com/gideonfip/keepable-clipper-templates) for quick additions to your Keepable vault.

---

## Folder structure

```
Keepable/
├── 0 - Reading/            # Reading-related Base files (All Links, Favourites, Highlights, Read Later)
├── 1 - Inbox/              # Default inbox for quick capture
├── 2 - Source Materials/   # All clipped content, organized by type
│   ├── Books/              # Book notes and highlights
│   ├── GitHub/             # GitHub repository readmes
│   ├── Highlights DB/      # Auto-generated highlight records
│   ├── Journal/            # Daily journal entries
│   ├── Landing Pages/      # Product/sales pages
│   ├── LinkedIn/           # LinkedIn posts
│   ├── Long-Form/          # Articles, essays, Substack, Medium
│   ├── Reddit/             # Reddit posts
│   ├── Resources/          # Tools, references, documentation
│   ├── Substack Notes/     # Substack short-form notes
│   ├── X Tweets/           # Short X/Twitter posts
│   └── YouTube/            # YouTube videos with transcripts
├── 3 - Bases/              # Obsidian Bases database views (10 .base files)
├── 4 - Personal notes/     # Private personal notes (not synced to public repo)
├── Author/                 # Auto-generated author pages
├── .agents/skills/         # AI agent skill definitions (13 skills)
├── Dashboard.md            # Main dashboard with todo and missing links
├── convert_tags_to_kebab.cjs
└── package.json
```

## Note format

Every clipped note uses a consistent YAML frontmatter:

```yaml
---
title: "Article Title"
source: "https://original-url.com"
author:
  - "[[Author Name]]"
published: 2025-01-15
created: 2025-01-15
description: "Brief description of the content"
tags:
  - defuddle
favourites: false
read-later: false
---
```

This makes every note queryable via Obsidian Bases or Dataview.

## Obsidian Bases

The `0 - Reading/` and `3 - Bases/` folders contain database views for every content type. Open any `.base` file in Obsidian to see a live, filterable table of your notes.

### 0 - Reading/ (reading workflow)

| Base | What it shows |
|------|--------------|
| `All Links` | Master index of all content across every source folder |
| `Favourites` | All bookmarked and favourite content |
| `Highlights Database` | All `==highlighted==` text across the vault with clickable source links |
| `Read Later` | Content queued for reading with read-later status |

### 3 - Bases/ (content indexes)

| Base | What it shows |
|------|--------------|
| `Authors` | All authors with linked article counts |
| `Dashboard items` | Todo items, recently modified, missing links |
| `Landing Pages Index` | All clipped landing pages |
| `LinkedIn` | All LinkedIn content |
| `Long-Form Index` | All articles, essays, Substack posts |
| `Resources Index` | All resource documents |
| `Substack Notes` | All Substack short-form content |
| `X Tweets Index` | All saved tweets |
| `YouTube Index` | All YouTube videos |

---

## AI Agent Skills

The `.agents/skills/` folder contains skill definitions for AI agents (Claude, Kiro, etc.). Each skill is a `SKILL.md` file that tells the agent exactly how to perform a task in this vault.

### Keepable skills

| Skill                         | What it does                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `keepable-clip`               | Clips a URL into the vault — fetches content, extracts metadata, creates the note in the right folder, creates/links the author page |
| `keepable-author`             | Creates and manages author pages from article metadata                                                                               |
| `keepable-tag`                | Analyzes content and adds appropriate tags following vault conventions                                                               |
| `keepable-link-cleaner`       | Standardizes X, LinkedIn, and Substack Notes filenames — matches title and filename to the description text                          |
| `keepable-yaml-cleaner`       | Audits and repairs YAML frontmatter to meet Obsidian Property standards                                                              |
| `keepable-highlight`          | Scans all notes for `==highlighted==` text and builds the Highlights Database                                                        |
| `fieldtheory-keepable-import` | Imports X/Twitter bookmarks from Field Theory (`ft`) into the vault with correct `YYYY-MM-DD` dates                                  |

### Obsidian reference skills

| Skill | What it does |
|-------|-------------|
| `obsidian-bases` | Reference documentation for Obsidian Bases syntax, formulas, and filters |
| `obsidian-markdown` | Reference for Obsidian-flavored Markdown (wikilinks, embeds, callouts, properties) |
| `obsidian-cli` | How to interact with the vault from the command line |
| `obsidian-defuddle` | How to use [defuddle](https://github.com/kepano/defuddle) for content extraction |
| `obsidian-json-canvas` | Reference for Obsidian Canvas JSON format |

### How to use skills

Point your AI agent at this vault and reference a skill by name:

```
skill keepable-clip
Clip this URL: https://example.com/article
```

The agent will read the `SKILL.md` file and follow the instructions to complete the task.

---

## Highlights

Any text wrapped in `==double equals==` becomes a highlight in Obsidian. The `keepable-highlight` skill scans the entire vault and builds a queryable database of every highlight, linked back to its source note.

Run the highlight refresh script from the vault root:

```bash
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py"
```

Or specify a vault path:

```bash
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py" --vault /path/to/vault
```

Options:
- `--dry-run` — Scan and count highlights without writing files
- `--full-rebuild` — Force full rebuild instead of incremental sync

---

## Tag normalizer

The `convert_tags_to_kebab.cjs` script converts all tags in the vault to kebab-case (e.g., `vibe_code` → `vibe-code`, `Content Strategy` → `content-strategy`).

Run from the vault root:

```bash
npm install
node convert_tags_to_kebab.cjs
```

Set `VAULT_PATH` to point to a different location:

```bash
VAULT_PATH=/path/to/your/vault node convert_tags_to_kebab.cjs
```

---

## Field Theory import

If you use [Field Theory](https://github.com/afar1/fieldtheory-cli) to bookmark X/Twitter posts, the `fieldtheory-keepable-import` skill can batch-import them into your vault with correct dates.

On first use, the agent will ask for your vault path, browser preference (chrome, brave, firefox, edge), and import mode. The script stores a cursor to only import new bookmarks on subsequent runs.

```bash
python3 .agents/skills/fieldtheory-keepable-import/scripts/import_fieldtheory_to_keepable.py \
  --vault /path/to/vault \
  --sync --browser chrome \
  --since-last-sync
```

For a manual backfill window:

```bash
python3 .agents/skills/fieldtheory-keepable-import/scripts/import_fieldtheory_to_keepable.py \
  --vault /path/to/vault \
  --sync --browser chrome \
  --after 2026-01-01
```

---

## Getting started

1. Download and install [Obsidian](https://obsidian.md)
2. Clone or download this repo
3. Open Obsidian → "Open folder as vault" → select this folder
4. Enable community plugins: Settings → Community plugins → enable `Reader Highlighter Tags` and `Style Settings`
5. Open `Dashboard.md` to see your todo items
6. Browse `0 - Reading/All Links.base` to see all content
7. Start clipping with the `keepable-clip` skill or the [web clipper templates](https://github.com/gideonfip/keepable-clipper-templates)

---

## Requirements

- [Obsidian](https://obsidian.md) (free)
- [Obsidian Bases](https://obsidian.md/bases) — built into Obsidian, no plugin needed (core plugin must be enabled)
- [defuddle](https://github.com/kepano/defuddle) — CLI for content extraction (used by `keepable-clip`)
- Node.js — for the tag normalizer script (`convert_tags_to_kebab.cjs`)
- Python 3 — for the highlights refresh and Field Theory import scripts

---

## Credits

Inspired by the following libraries:

- [PenguinVault](https://github.com/frogpal/PenguinVault) by frogpal
- [Obsidian Skills](https://github.com/kepano/obsidian-skills) by kepano
- [Reader Highlighter Tags](https://github.com/DuckTapeKiller/obsidian-reader-highlighter-tags) by DuckTapeKiller

## Notes

Keepable can be used together with the [Portable AI System](https://portable.gideonfip.com/).
