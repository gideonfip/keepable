---
name: keepable-highlight
description: "Build and refresh a vault-wide Obsidian Highlights database from ==...== and ====...==== markers. Use this whenever the user asks to collect all highlights, rebuild highlight tables after edits, create a single highlights database, or make clickable highlight-to-article links in Bases."
---
user-invokable: true
disable-model-invocation: false

# Obsidian Highlights

Create a single, refreshable highlight database across the vault.

## What this skill does

1. Scans markdown notes under `2 - Source Materials/`
2. Extracts highlights marked as `==...==` or `====...====`
3. Incrementally syncs generated notes in `2 - Source Materials/Highlights DB/`
4. Writes/updates `0 - Reading/Highlights Database.base`

Each generated highlight note includes:
- `name`
- `highlight`
- `author`
- `date`
- `source_note`

## Trigger guidance

Use this skill when the user says things like:
- "show all my highlights"
- "make a highlights database"
- "refresh highlights after edits"
- "I removed some highlights, sync the table"
- "make highlight names clickable to the source article"

## Run

From the vault root, run:

```bash
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py"
```

Optional flags:

```bash
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py" --dry-run
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py" --full-rebuild
python3 ".agents/skills/keepable-highlight/scripts/refresh_highlights_db.py" --vault "/absolute/path/to/vault"
```

## Important behavior

- Default mode is incremental sync (add/update/remove only where source notes changed).
- Use `--full-rebuild` to force a destructive rebuild of all generated records.
- Only markdown files under `2 - Source Materials/` are scanned.
- Existing user-authored notes outside `Highlights DB/` are never modified.

## Expected outputs

- `2 - Source Materials/Highlights DB/*.md` generated records
- `0 - Reading/Highlights Database.base` with clickable Name links via formula
