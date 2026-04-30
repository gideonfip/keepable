---
aliases:
  - Tiago Forte
---

# Tiago Forte

## Content

```dataview
TABLE
  file.folder AS "Category",
  published AS "Published",
  description AS "Description"
FROM "2 - Source Materials"
WHERE contains(author, "Tiago Forte")
SORT published DESC
```
