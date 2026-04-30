---
aliases:
  - "@gideonfip"
---

# @gideonfip

## Content

```dataview
TABLE
  file.folder AS "Category",
  published AS "Published",
  description AS "Description"
FROM "2 - Source Materials"
WHERE contains(author, "@gideonfip")
SORT published DESC
```
