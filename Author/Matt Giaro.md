---
aliases:
  - Matt Giaro
---

# Matt Giaro

## Content

```dataview
TABLE
  file.folder AS "Category",
  published AS "Published",
  description AS "Description"
FROM "2 - Source Materials"
WHERE contains(author, "Matt Giaro")
SORT published DESC
```
