---
name: keepable-author
description: "Organize and manage author files in an Obsidian vault. Use this skill when the user wants to: create author pages from article metadata, extract unique authors from an Obsidian database, manage the Author folder, or link articles to their author pages. Triggers on: 'organize authors', 'author files', 'create author pages', 'extract authors from vault', 'manage Author folder', 'link mentions to authors', 'build author database'."
---
user-invokable: true
disable-model-invocation: false

# Obsidian Author Skill

Create and manage author files in an Obsidian vault, linking articles to their authors via wikilinks and Obsidian's native backlinks system.

## Critical Rules (Learn From Mistakes)

### Rule 1: Match Exact Author Names
**ALWAYS use the exact author name from the `author` field in articles**, not transformed versions.

- Articles use: `author: - "[[Author Name]]"`
- Author file name must be: `Author/Author Name.md` (exact match)
- Dataview query must use: `WHERE contains(author, "Author Name")` (exact match)

**NEVER transform author names by:**
- Adding or removing `@` prefixes
- Replacing spaces with `_`
- Changing capitalization
- Using sanitized/encoded versions

### Rule 2: Preserve X/Twitter Handles Exactly
If article metadata uses `[[@username]]`, create `Author/@username.md` and query `WHERE contains(author, "@username")`.

If article metadata uses `[[username]]`, create `Author/username.md` and query `WHERE contains(author, "username")`.

Do not strip `@`. The author metadata is the source of truth.

Exception: if an author wikilink contains `/`, repair the article metadata to an existing page-safe author name first, because `/` creates folders in paths and cannot be used as a single author filename.

### Rule 3: Create All Authors From Article Metadata
Always extract author names from the `author` field in articles within `2 - Source Materials/` folder. Do not manually maintain a separate list.

## Workflow

### Step 1: Extract Unique Authors And Missing Pages
Use the one-pass scanner below instead of `grep` globbing. It reads only frontmatter, handles both inline and list-style `author` fields, mirrors the folders in `0 - Reading/📎 All Links.base`, and compares exact author names to `Author/*.md` filenames.

```bash
ruby -e 'require "find"; sources=["2 - Source Materials/Landing Pages","2 - Source Materials/Long-Form","2 - Source Materials/Substack Notes","2 - Source Materials/X Articles","2 - Source Materials/X Tweets","2 - Source Materials/LinkedIn","2 - Source Materials/YouTube","2 - Source Materials/Resources","2 - Source Materials/Premium Emails","2 - Source Materials/Write With AI"]; authors=Hash.new{|h,k| h[k]=[]}; sources.each{|dir| next unless Dir.exist?(dir); Find.find(dir){|p| next unless p.end_with?(".md"); text=File.binread(p).force_encoding("UTF-8").scrub; fm=text[/\A---\n(.*?)\n---/m,1]; next unless fm; in_author=false; fm.lines.each{|line| if line =~ /^author:\s*(.*)$/; in_author=true; $1.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; next; end; if in_author; if line =~ /^\s+-\s+/; line.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; else; in_author=false; end; end } }}; existing={}; Dir.glob("Author/*.md"){|p| existing[File.basename(p,".md")]=true}; missing=authors.keys.reject{|a| existing[a]}.sort; puts "unique_authors=#{authors.size}"; puts "author_files=#{existing.size}"; puts "missing=#{missing.size}"; missing.each{|a| puts a }'
```

This outputs all missing author page names exactly as they appear in article metadata.

When troubleshooting, separate true missing pages from case-only mismatches. On macOS, case-only filename mismatches can look missing to an exact scanner even though Obsidian resolves the page.

```bash
ruby -e 'require "find"; sources=["2 - Source Materials/Landing Pages","2 - Source Materials/Long-Form","2 - Source Materials/Substack Notes","2 - Source Materials/X Articles","2 - Source Materials/X Tweets","2 - Source Materials/LinkedIn","2 - Source Materials/YouTube","2 - Source Materials/Resources","2 - Source Materials/Premium Emails","2 - Source Materials/Write With AI"]; authors=Hash.new{|h,k| h[k]=[]}; sources.each{|dir| next unless Dir.exist?(dir); Find.find(dir){|p| next unless p.end_with?(".md"); text=File.binread(p).force_encoding("UTF-8").scrub; fm=text[/\A---\n(.*?)\n---/m,1]; next unless fm; in_author=false; fm.lines.each{|line| if line =~ /^author:\s*(.*)$/; in_author=true; $1.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; next; end; if in_author; if line =~ /^\s+-\s+/; line.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; else; in_author=false; end; end } }}; files=Dir.glob("Author/*.md").map{|p| File.basename(p,".md")}; case_only=[]; missing=[]; authors.keys.sort.each{|a| if files.include?(a); next; elsif (match=files.find{|f| f.downcase == a.downcase}); case_only << [a,match]; else; missing << a; end}; puts "unique_authors=#{authors.size}"; puts "author_files=#{files.size}"; puts "missing=#{missing.size}"; puts "case_only=#{case_only.size}"; missing.each{|a| puts "MISSING #{a}"}; case_only.each{|a,m| puts "CASE #{a} -> #{m}"}'
```

Create pages for `MISSING` entries. For `CASE` entries, either leave them if Obsidian resolves them or standardize the article metadata to the existing author filename.

To see source files for a specific missing author, run:

```bash
ruby -e 'require "find"; wanted=ARGV[0]; sources=["2 - Source Materials/Landing Pages","2 - Source Materials/Long-Form","2 - Source Materials/Substack Notes","2 - Source Materials/X Articles","2 - Source Materials/X Tweets","2 - Source Materials/LinkedIn","2 - Source Materials/YouTube","2 - Source Materials/Resources","2 - Source Materials/Premium Emails","2 - Source Materials/Write With AI"]; sources.each{|dir| next unless Dir.exist?(dir); Find.find(dir){|p| next unless p.end_with?(".md"); text=File.binread(p).force_encoding("UTF-8").scrub; fm=text[/\A---\n(.*?)\n---/m,1]; puts p if fm&.include?("[[#{wanted}]]") }}' '@fern'
```

### Step 2: Create Author Files
For each unique author name:
1. Create file at `Author/<Author Name>.md`
2. Use the EXACT author name (preserve spaces, capitalization, special characters)
3. Generate Dataview query with EXACT match

### Step 3: Author File Template

```markdown
---
aliases:
  - <Author Name>
---

# <Author Name>

## Content

\`\`\`dataview
TABLE
  file.folder AS "Category",
  published AS "Published",
  description AS "Description"
FROM "2 - Source Materials"
WHERE contains(author, "<Author Name>")
SORT published DESC
\`\`\`
```

### Step 4: Create Author Database (Optional)
Create `Author/Authors.base` for a database view:

```yaml
name: Authors Database
description: Database of all authors with their articles

filters:
  - file.inFolder("Author")

formulas:
  article_count: 'file.links.filter(l => l.path.contains("2 - Source Materials")).length'

properties:
  file.name:
    displayName: Author
  formula.article_count:
    displayName: Articles

summaries:
  formula.article_count:
    - Sum
    - Average
    - Max

views:
  - type: table
    name: All Authors
    order:
      - file.name
      - formula.article_count

  - type: cards
    name: Author Cards
    order:
      - file.name
      - formula.article_count
```

## Common Mistakes to Avoid

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| Stripping `@` from handles | It breaks exact matching for `[[@user]]` metadata | Preserve `[[@user]]` and create `Author/@user.md` |
| Using `_` prefix | Underscore prefix makes files look system-generated | Match exact author name without prefixes |
| Transforming names | Dataview queries use exact string matching | Use `WHERE contains(author, "Exact Name")` |
| Manual author list | Authors change; metadata is source of truth | Always extract from article `author` field |

## Quick Command Reference

```bash
# Extract missing authors from articles
ruby -e 'require "find"; sources=["2 - Source Materials/Landing Pages","2 - Source Materials/Long-Form","2 - Source Materials/Substack Notes","2 - Source Materials/X Articles","2 - Source Materials/X Tweets","2 - Source Materials/LinkedIn","2 - Source Materials/YouTube","2 - Source Materials/Resources","2 - Source Materials/Premium Emails","2 - Source Materials/Write With AI"]; authors=Hash.new{|h,k| h[k]=[]}; sources.each{|dir| next unless Dir.exist?(dir); Find.find(dir){|p| next unless p.end_with?(".md"); text=File.binread(p).force_encoding("UTF-8").scrub; fm=text[/\A---\n(.*?)\n---/m,1]; next unless fm; in_author=false; fm.lines.each{|line| if line =~ /^author:\s*(.*)$/; in_author=true; $1.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; next; end; if in_author; if line =~ /^\s+-\s+/; line.scan(/\[\[([^\]]+)\]\]/){|m| authors[m[0]] << p}; else; in_author=false; end; end } }}; existing={}; Dir.glob("Author/*.md"){|p| existing[File.basename(p,".md")]=true}; missing=authors.keys.reject{|a| existing[a]}.sort; puts "unique_authors=#{authors.size}"; puts "author_files=#{existing.size}"; puts "missing=#{missing.size}"; missing.each{|a| puts a }'

# Check if author file exists for a specific author
ls "Author/<Author Name>.md"
```

## Verification Steps

After creating author files:
1. Check that `Author/<Name>.md` exists for at least one known article author
2. Verify Dataview query returns the correct articles
3. Confirm backlinks appear in article files pointing to author pages

## Vault Structure Expected

```
Vault/
├── Author/                    # All author files
│   ├── <Author Name 1>.md
│   ├── <Author Name 2>.md
│   └── Authors.base           # Optional database
└── 2 - Source Materials/      # All articles with author metadata
    ├── X Articles/
    ├── YouTube/
    ├── Substack Notes/
    └── ...
```

The author field in articles should look like:
```yaml
author:
  - "[[Author Name]]"
```

For X/Twitter handles, preserve the exact wikilink used in metadata:

```yaml
author:
  - "[[@username]]"
```
