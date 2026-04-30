---
name: keepable-tag
description: "Analyzes and adds tags to Obsidian notes based on existing tagging patterns in the vault. Use this skill when the user mentions 'add tags', 'tag articles', 'analyze tags', 'empty tags', 'find tagging patterns', or wants to add appropriate tags to untagged notes following vault conventions."
---
user-invokable: true
disable-model-invocation: false

# Obsidian Tag Skill

This skill analyzes existing tagging patterns in the Obsidian vault and applies appropriate tags to untagged or empty-tag notes. It ensures consistency with established vault conventions.

## Core Principles

### 1. Tag Format
- **Always use YAML list format** with `---` delimiters:
```yaml
tags:
  - tag1
  - tag2
  - tag3
---
```

### 2. Common Tags in This Vault (kebab-case)

Based on frequency analysis, these are the most used tags:

| Tag | Usage |
| :--- | :--- |
| `ai` | AI-related content, LLMs, agents |
| `ct` | Crypto Twitter opinions |
| `slop` | Low-quality AI output discussions |
| `vibe-code` | Coding workflows, AI development |
| `obsidian` | PKM, note-taking tools |
| `claude` | Claude-specific content |
| `writing` | Writing advice, content creation |
| `marketing` | Marketing strategies |
| `creator` | Creator economy |
| `business` | Business, entrepreneurship |
| `wealth` | Finance, money topics |
| `security` | Security, safety |
| `airdrop-thoughts` | Airdrop analysis |

### 3. Topic-Specific Tags (kebab-case)
- `airdrop-toxic`, `scam-ct` - Crypto scam warnings
- `info-fi` - InformationFi topics
- `reputation` - Personal reputation
- `local-llm` - Local model running
- `farming-airdrops` - Airdrop farming
- `content-strategy` - Content marketing
- `personal-brand` - Personal branding

## Workflow

### Step 1: Analyze Existing Tags
Run a frequency analysis to find common tags:
```bash
grep -h "^  - " "Long-Form"/*.md "X Tweets"/*.md 2>/dev/null | sort | uniq -c | sort -rn | head -30
```

### Step 2: Identify Files WITHOUT Frontmatter
Most files already have tags. Find files that have NO frontmatter at all (these need tags added):
```javascript
// Node.js approach
const fs = require('fs');
const content = fs.readFileSync(filePath, 'utf8');
const hasFrontmatter = content.trim().startsWith('---');
if (!hasFrontmatter) {
  // Add tags here - file has no frontmatter
}
```

**Important**: Files with `title:`, `source:`, `author:` already have frontmatter - skip them!

### Step 3: Determine Appropriate Tags (kebab-case)
Based on the article content:
- **AI articles** → `ai`, `workflow`, `vibe-code`
- **Crypto opinions** → `ct`, `airdrop-thoughts`
- **Writing advice** → `writing`, `content-strategy`
- **Business/Entrepreneurship** → `business`, `creator`
- **Finance** → `wealth`, `finance`
- **Tools (Obsidian, Claude)** → `obsidian`, `vibe-code`
- **Quality warnings** → `slop`, `ct`

### Step 4: Apply Tags - SAFE METHOD

**CRITICAL: Always check for existing frontmatter before adding tags!**

Use this Node.js script approach to safely add tags:

```javascript
const fs = require('fs');

function addTagsSafely(filePath, tags) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  
  // Check if file starts with --- (has frontmatter)
  const hasFrontmatter = content.trim().startsWith('---');
  
  // If already has frontmatter, add tags to existing block
  if (hasFrontmatter) {
    // Find where tags: line is or insert before closing ---
    let tagInserted = false;
    const newLines = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      newLines.push(line);
      
      // If this is the tags: line with no value, fill it
      if (line.match(/^tags:\s*$/)) {
        // Check next line - if empty, add tags
        if (i + 1 < lines.length && lines[i + 1].trim() === '') {
          newLines.push(`  - ${tags.join('\n  - ')}`);
          tagInserted = true;
        }
      }
    }
    
    if (!tagInserted) {
      // Insert tags at start of frontmatter
      newLines.splice(1, 0, `tags:\n  - ${tags.join('\n  - ')}`);
    }
    fs.writeFileSync(filePath, newLines.join('\n'));
  } else {
    // No frontmatter - create new with tags
    const newContent = `---
tags:
  - ${tags.join('\n  - ')}
---

${content}`;
    fs.writeFileSync(filePath, newContent);
  }
}
```

**NEVER do this (creates duplicate frontmatter):**
```yaml
---
tags:
  - ct
---
---
title: "Some title"
```

**ALWAYS do this (append to existing frontmatter):**
```yaml
---
title: "Some title"
tags:
  - ct
---
```

## Instructions for Claude

When triggered, you should:
1. **Acknowledge** the request and confirm you'll analyze tagging patterns
2. **Analyze** existing tags or identify files WITHOUT frontmatter
3. **NEVER add tags to files that already have frontmatter** - skip them
4. **Only add tags to files with no frontmatter at all** - create properly formatted YAML
5. **Report** success with a summary of files modified

**Safety Rule**: If a file has `title:`, `source:`, `author:`, or any other frontmatter field, DO NOT add new tags to it - it already has frontmatter and should already have tags.

## Triggering Phrases
- "add tags to articles"
- "analyze tagging patterns"
- "find empty tags"
- "tag untagged notes"
- "fix tags"
- "what tags are used most"
- "bulk tag"