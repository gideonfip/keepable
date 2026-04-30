---
name: keepable-yaml-cleaner
description: "Cleans, formats, and validates Obsidian YAML frontmatter to ensure strict adherence to official Obsidian property standards. Use this skill whenever a user mentions 'clean YAML', 'fix frontmatter', 'format properties', 'YAML error', 'fix quotes', 'invalid property', or wants to ensure their notes are properly structured for Dataview and Obsidian search. Make sure to use this skill whenever you notice unescaped quotes in titles, incorrect wikilink formats in lists, or non-standard date/number formats in frontmatter."
---
user-invokable: true
disable-model-invocation: false

# Obsidian YAML Clean Skill

This skill is designed to audit and repair the YAML frontmatter of Obsidian notes, ensuring they comply with the official Obsidian Property standards. It aims to make the vault machine-readable (for Dataview, search, etc.) and human-readable.

## Core Standards (The "Source of Truth")

The skill must strictly follow these rules derived from the official Obsidian documentation:

### 1. General Formatting
- **Syntax**: `property: value` (with a space after the colon).
- **Uniqueness**: Each property name must be unique within a single note.
- **Wrapping**: Use `---` at the very beginning and end of the frontmatter block.

### 2. Property Types & Formatting
| Type | Rule | Correct Example | Incorrect Example |
| :--- | :--- | :--- | :--- |
| **Text** | Use quotes for strings containing special characters or links. | `title: "My \"Quote\""` | `title: "My "Quote""` |
| **Wikilinks (Text)** | Must be surrounded by double quotes. | `link: "[[Page Name]]"` | `link: [[Page Name]]` |
| **Lists** | Each item on a new line with a hyphen. | `tags: `<br>`  - tag1`<br>`  - tag2` | `tags: [tag1, tag2]` |
| **Wikilinks (List)** | Each link on a new line, preceded by hyphen AND in quotes. | `author:`<br>`  - "[[Name]]"` | `author:`<br>`  - [[Name]]` |
| **Number** | Must be a literal number (no quotes, no expressions). | `year: 2026` | `year: "2026"` |
| **Checkbox** | Must be `true` or `false`. | `favorite: true` | `favorite: "yes"` |
| **Date** | Must follow `YYYY-MM-DD` format. | `date: 2026-04-24` | `date: April 24, 2026` |

## Workflow

### Step 1: Audit
Examine the YAML frontmatter of the target file(s) and identify:
1. **Syntax errors**: Unescaped quotes in titles or strings.
2. **Link errors**: Wikilinks missing quotes in text or list properties.
3. **Type errors**: Numbers in quotes, non-standard dates, or non-boolean checkboxes.
4. **List errors**: Improperly formatted list properties.

### Step 2: Repair
Apply the corrections based on the "Core Standards" table above.
- **Fixing Titles**: Escape internal quotes using `\"`.
- **Fixing Links**: Ensure all `[[Link]]` instances in properties are wrapped in `" "`.
- **Fixing Types**: Strip quotes from numbers, convert date strings to `YYYY-MM-DD`, and ensure checkboxes are `true`/`false`.

### Step 3: Verification (The "Audit Check")
After applying changes, perform a final verification pass:
1. **Syntax Check**: Does the YAML still parse correctly? (No unmatched quotes).
2. **Type Check**: Are the properties now the correct type (Number, Date, etc.)?
3. **Link Check**: Are all wikilinks properly quoted?

## Instructions for Claude

When triggered, you should:
1. **Acknowledge** the request and summarize what errors you found (e.g., "I found 3 files with unescaped quotes in titles and 2 files with unquoted wikilinks in the author field.").
2. **Execute** the cleanup using tools (e.g., `edit` or `bash` with `perl/sed`).
3. **Report** success, clearly listing the files that were modified.
4. **Provide a "State of the Vault" summary**: A quick confirmation that the repaired files now comply with the Obsidian standard.

## Triggering Phrases
- "clean up the yaml"
- "fix the frontmatter"
- "format my properties"
- "fix quotes in my notes"
- "make my yaml valid"
- "obsidian yaml error"
- "fix my wikilinks in properties"
