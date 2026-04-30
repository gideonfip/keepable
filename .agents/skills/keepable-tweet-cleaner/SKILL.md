---
name: keepable-tweet-cleaner
description: "Clean up X (Twitter) post files by standardizing their title, description, and filename. Use this skill when you want to match the filename and title to the description in your X Tweets folder, ensuring that special characters like ':', '/', and '\\' are removed from the filename."
---
user-invokable: true
disable-model-invocation: false

# Obsidian Tweet Cleaner

This skill standardizes X (Twitter) post files in your Obsidian vault. It ensures that the file's title, description, and filename are all consistent and free of problematic characters.

## Workflow

When triggered, this skill will:

1. **Search**: Find all Markdown files in the vault's `2 - Source Materials/X Tweets/` folder that follow the naming pattern `Post by @[username] on X.md`. On first use, ask the user for their vault path.
2. **Analyze**: For each matching file:
    - Read the file's YAML frontmatter.
    - Extract the value of the `description` field.
3. **Clean**: Create a "sanitized" version of that description by:
    - Removing the following characters: `:` (colon), `/` (forward slash), `\` (backslash)
    - Truncating to approximately 100 characters, but **always completing the last word** — even if this means exceeding 100 characters slightly. Never cut a word mid-way. If truncation would split a word, extend to the end of that word. If the sanitized description is already under 100 characters, use it in full.
4. **Update**:
    - Set the `title` field in the YAML frontmatter to the sanitized excerpt.
    - Set the `description` field in the YAML frontmatter to the sanitized excerpt.
5. **Rename**: Rename the file to `[sanitized_excerpt].md`.

## Examples

**Input File**: `Post by @itsolelehmann on X.md`
**YAML Content**:
```yaml
---
title: "i built a free claude skill on the most critical content principle in 2026: The Minto Pyramid (from"
description: "i built a free claude skill on the most critical content principle in 2026: The Minto Pyramid (from a 1970s McKinsey book on clear communic"
...
---
```

**Action**:
1. Sanitized excerpt: `i built a free claude skill on the most critical content principle in 2026 The Minto Pyramid (from a 1970s McKinsey book on clear communication`
   (note: the last word "communication" is completed even though it exceeds 100 characters slightly)
2. Update YAML `title` and `description`.
3. Rename file to `i built a free claude skill on the most critical content principle in 2026 The Minto Pyramid (from a 1970s McKinsey book on clear communication.md`.

## Triggering Context

Use this skill when:
- You have many files named `Post by @...` that you want to rename to their actual content.
- You want to ensure your X Tweets folder has consistent metadata and filenames.
- You see filenames or titles containing characters like `:`, `/`, or `\` that might cause issues in Obsidian or other tools.

## Also Run keepable-tag After Cleaning

After cleaning tweet files, you may want to run the keepable-tag skill to add appropriate tags based on content:

```bash
skill keepable-tag
```

This will analyze the now-cleaned titles and descriptions to add relevant tags like:
- `ai`, `vibe_code` for AI content
- `writing`, `content_strategy` for advice
- `business`, `creator` for entrepreneurship
- `ct` for Crypto Twitter
