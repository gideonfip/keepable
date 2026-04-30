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

### 2. Common Tags in This Vault

Based on frequency analysis, these are the most used tags:

| Tag | Usage |
| :--- | :--- |
| `ai` | AI-related content, LLMs, agents |
| `ct` | Crypto Twitter opinions |
| `slop` | Low-quality AI output discussions |
| `vibe_code` | Coding workflows, AI development |
| `obsidian` | PKM, note-taking tools |
| `claude` | Claude-specific content |
| `writing` | Writing advice, content creation |
| `marketing` | Marketing strategies |
| `creator` | Creator economy |
| `business` | Business, entrepreneurship |
| `wealth` | Finance, money topics |
| `security` | Security, safety |
| `airdrop_thoughts` | Airdrop analysis |

### 3. Topic-Specific Tags
- `airdrop_toxic`, `scam_ct` - Crypto scam warnings
- `infofi` - InformationFi topics
- `reputation` - Personal reputation
- `local_llm` - Local model running
- `farming_airdrops` - Airdrop farming

## Workflow

### Step 1: Analyze Existing Tags
Run a frequency analysis to find common tags:
```bash
grep -h "^  - " "Long-Form"/*.md "X Tweets"/*.md 2>/dev/null | sort | uniq -c | sort -rn | head -30
```

### Step 2: Identify Empty Tags
Find files with empty or missing tags:
```bash
for f in *.md; do if grep -q "^tags:$" "$f" && ! grep -A1 "^tags:" "$f" | grep -q "  -"; then echo "$f"; fi; done
```

### Step 3: Determine Appropriate Tags
Based on the article content:
- **AI articles** → `ai`, `workflow`, `vibe_code`
- **Crypto opinions** → `ct`, `airdrop_thoughts`
- **Writing advice** → `writing`, `content_strategy`
- **Business/Entrepreneurship** → `business`, `creator`
- **Finance** → `wealth`, `finance`
- **Tools (Obsidian, Claude)** → `obsidian`, `vibe_code`
- **Quality warnings** → `slop`, `ct`

### Step 4: Apply Tags
Use the `edit` tool to replace empty tags:
```yaml
# Before:
tags:

# After:
tags:
  - ai
  - workflow
  - vibe_code
---
```

**Important**: Always keep the closing `---` delimiter!

## Instructions for Claude

When triggered, you should:
1. **Acknowledge** the request and confirm you'll analyze tagging patterns
2. **Analyze** existing tags or identify empty-tag files
3. **Determine** appropriate tags based on content and vault patterns
4. **Apply** tags using the `edit` tool with proper YAML format
5. **Report** success with a summary of files modified

## Triggering Phrases
- "add tags to articles"
- "analyze tagging patterns"
- "find empty tags"
- "tag untagged notes"
- "fix tags"
- "what tags are used most"
- "bulk tag"
