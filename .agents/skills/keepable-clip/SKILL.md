---
name: keepable-clip
description: "Clip web content (articles, tweets, YouTube videos, Substack posts, landing pages) into an Obsidian vault using defuddle. Use this skill whenever the user wants to save a URL, clip web content, add a link to their vault, capture an article, save a tweet, or archive online content. Also trigger when the user mentions clipping, saving links, web capture, content curation, or building a reading database."
---
user-invokable: true
disable-model-invocation: false

# Obsidian Clipper

Clip web content into an organized Obsidian vault with full metadata extraction, author linking, and database indexing.

## Workflow

### 1. Determine Vault Path

On first use, ask the user for their Obsidian vault path. The vault root is the folder containing `.obsidian/`, `2 - Source Materials/`, `3 - Bases/`, and `Author/`. Store this path and use it for all subsequent operations.

### 2. Determine Content Type

From the URL, determine which category folder to use:

| URL Pattern | Category Folder |
|-------------|----------------|
| x.com, twitter.com | X Tweets/ (short) or X Articles/ (long threads) |
| reddit.com | Reddit/ |
| github.com | GitHub/ |
| youtube.com, youtu.be | YouTube/ |
| substack.com, medium.com | Long-Form/ |
| Other domains, long articles | Long-Form/ |
| Landing pages, product pages, sales pages (<100 words) | Landing Pages/ |

**Classification rules:**
- **X/Twitter**: Short posts (<300 words or single image/video) → `X Tweets/`. Long threads/essays → `X Articles/`.
- **Reddit**: All Reddit posts → `Reddit/`
- **GitHub**: All GitHub repos/readmes → `GitHub/`
- **YouTube**: All videos → `YouTube/`
- **Substack/Medium**: All → `Long-Form/`
- **Other domains** (blogs, news, essays): → `Long-Form/`
- **Short pages** (<100 words, mostly copy/pitch): → `Landing Pages/`
- **Never put non-X content into X Articles/** — only X long-form threads go there.

### 3. Extract Content with Defuddle

Always use defuddle with `--md` flag to get clean markdown output:

```bash
defuddle parse "<URL>" --md
```

**CRITICAL — Preserve markdown formatting**: defuddle already produces clean markdown with proper formatting. **Never strip markdown syntax** (bold `**text**`, headers `###`, wikilinks, etc.). The transcript from defuddle for YouTube already includes `**0:00** ·` timestamps and `### Chapter` headers — preserve these exactly as defuddle outputs them.

**Only strip HTML if truly needed**: If the defuddle output contains a raw `<article data-defuddle="">` HTML wrapper, use a proper HTML-to-markdown converter (e.g. `turndown` or regex that only strips actual HTML tags `<...>`) — never blindly strip all angle brackets or special characters. In practice, current defuddle (v0.18+) rarely produces HTML wrappers.

Extract these metadata fields from defuddle's output:
- `title` — clipped title
- `author` — channel/creator name
- `description` — video/page description
- `published` — publication date (or `date` as fallback)
- `source` — the original URL
- `cover` — thumbnail/OG image URL

For YouTube videos where published is empty, fetch the date from the page:
```bash
curl -s "<youtube-url>" | grep -o '"dateText":{"simpleText":"[^"]*"' | head -1
```

**For YouTube Shorts specifically**, the above method may not work. Use this instead:
```bash
curl -sL "https://www.youtube.com/shorts/<VIDEO_ID>" | tr ';' '\n' | grep -E '"uploadDate"|"datePublished"' | head -2
```
If `uploadDate` is not found, try extracting from the OpenGraph metadata:
```bash
curl -sL "https://www.youtube.com/shorts/<VIDEO_ID>" | tr '"' '\n' | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1
```

### 4. Determine Title

For X/Twitter posts with generic titles like "Post by @username on X":
- Use the description or first line of content as the title instead
- Example: Instead of "Post by @aiwithmayank on X", use "I just deleted iTerm2, Warp, and Ghostty from my Mac..."

For all other content: Use the defuddle title

### 5. Check for Duplicates

Before creating a file, check if the content already exists in the vault by searching for the `source` URL:
```bash
grep -r "<source-url>" "<vault-path>" --include="*.md" -l
```
- If a match is found, **do not create a new file** — inform the user that this content was already clipped.
- If no match is found, proceed to Step 6.

### 6. Create Frontmatter

Take the frontmatter directly from defuddle output. Always add `tags`, `favourites`, and `read-later` fields to every new entry.

Always include `tags` with at least the `defuddle` tag. If defuddle output includes additional tags, add them too:
```yaml
tags:
  - defuddle
```

Always include `favourites` defaulting to false:
```yaml
favourites: false
```

Always include `read-later` defaulting to false:
```yaml
read-later: false
```

```yaml
---
title: "The Actual Title"
source: "https://original-url.com"
author:
  - "[[Author Name]]"
published: YYYY-MM-DD
created: YYYY-MM-DD
description: "The description from defuddle or first few sentences"
tags:
  - defuddle
favourites: false
read-later: false
---
```

Important:
- author must be a wikilink array: [[Author Name]]
- source must be quoted
- title must be quoted
- created is today's date
- published comes from defuddle (not date field)
- Always add `tags` with at least `defuddle`
- Always add `favourites: false`
- Always add `read-later: false`

### 7. Save to Vault

Save to the appropriate folder under `2 - Source Materials/`:
- X Articles/
- X Tweets/
- Long-Form/
- Reddit/
- GitHub/
- YouTube/
- Landing Pages/

If a file with the same name already exists, overwrite it (do not create duplicates like `(1)`, `(2)`).

### 8. Create/Link Author Page

Check if author already exists in `Author/` folder:
- If exists: just use the wikilink [[Author Name]]
- If new: create `Author/<Author Name>.md` with Dataview query

### 9. Update Database (Base)

Each category has a `.base` file in `3 - Bases/` that auto-indexes content.

### 3b. YouTube Post-Processing

After defuddle extraction, apply these YouTube-specific formatting steps:

**A. Format the description** (the text between the video embed and `## Transcript`):
- Split on emoji markers (🔴, 😀, 📺, ▬, 🎬) by inserting double-newline before each
- Format chapter timestamps as a readable list:
  ```
  00:00 Question 1
  02:49 Question 2
  ...
  ```
- If the description ends with `...` (truncated), replace the body description with the frontmatter `description` field content for the full text
- Preserve `Related videos` sections with their links

**B. Add cover image at bottom** — append after the transcript:
```markdown
![](https://i.ytimg.com/vi/<VIDEO_ID>/maxresdefault.jpg)
```
Extract `<VIDEO_ID>` from the URL (e.g. `9CM5uO2fXWg` from `watch?v=9CM5uO2fXWg`).

**C. Preserve transcript formatting** — defuddle's YouTube transcript output already includes:
- `### Question N` / chapter headers
- `**0:00** ·` timestamp markers at segment boundaries
- Proper paragraph grouping

**Do NOT modify the transcript at all** — keep all timestamps, headers, and line breaks exactly as defuddle outputs them.

## Special Cases

- X/Twitter Threads vs Single Tweets: Long threads go to X Articles/, short posts to X Tweets/
- YouTube Videos: **Keep defuddle transcript as-is** with timestamps and chapter headers. Format description section with line breaks (see 3b). Add cover image at bottom.
- YouTube Shorts: For published date, the standard defuddle extraction may not work. Use the Shorts-specific curl commands in Step 3 to fetch the upload date. Extract full transcript.
- Reddit Posts: Treat as Reddit/ category, not X Articles/
- GitHub Repos: Treat as GitHub/ category
- Non-X blogs/articles: Always go to Long-Form/, never X Articles/

## Common Mistakes to Avoid

1. Don't truncate content — use full transcripts from defuddle
2. Don't forget author wikilinks — must be [[Author Name]] format
3. Don't mix up published vs created
4. Don't skip author pages — always create/link in Author/ folder
5. Don't use description as generic title for X posts
6. Don't forget to quote strings in frontmatter
7. Don't create duplicate files — overwrite existing files instead
8. Don't put non-X content in X Articles/ — only X long-form threads belong there
9. Don't forget to add `tags` with at least `defuddle` to every new entry
10. Don't forget to add `favourites: false` to every new entry
11. Don't forget to add `read-later: false` to every new entry
12. Don't leave published empty for YouTube Shorts — use the Shorts-specific curl commands to fetch the upload date
13. Don't clip content that's already in the vault — always check for duplicate source URLs first
14. **NEVER strip markdown formatting** from defuddle output — timestamps (`**0:00** ·`), headers (`###`), bold, links, etc. must be preserved. Only strip actual HTML tags if an `<article>` wrapper exists, and only the HTML tags themselves, not markdown syntax.
15. **Don't use `cd ~/defuddle && node dist/cli.js`** — defuddle is installed globally via npm, use just `defuddle parse "<URL>" --md`

### 10. Post-Clip Processing (Optional)

After clipping, you can optionally run these skills:

#### A. Run keepable-tag to add appropriate tags

After clipping content, run the keepable-tag skill to analyze the content and add appropriate tags based on vault conventions:

This will add tags like:
- `ai`, `vibe_code` for AI-related content
- `writing`, `content_strategy` for writing advice
- `business`, `creator` for entrepreneurship topics
- `wealth`, `finance` for money topics
- `obsidian` for PKM/tool content

#### B. Run keepable-tweet-cleaner for X posts

For X/Twitter posts with generic titles like "Post by @username on X", run the keepable-tweet-cleaner skill to rename files to their actual description:

This will:
1. Find files named `Post by @username on X`
2. Extract the `description` from frontmatter
3. Sanitize special characters (: / \)
4. Update title/description and rename file to the content

Example:
- Before: `Post by @bcherny on X.md` with title "Post by @bcherny on X"
- After: `I just deleted iTerm2, Warp, and Ghostty from my Mac...` with actual description
