
# Fatcat "Chocula" Journal Metadata Summary

This report is auto-generated from a sqlite database file, which should be available/included.

```sql
SELECT datetime('now');
```

Note that pretty much all of the fatcat release stats are on a *release*, not
*work* basis, so there may be over-counting. Also, as of July 2019 there were
over 1.5 million OA longtail releases which are *not* linked to a container
(journal).

```sql
PRAGMA database_list;
```

## Overview

Top publishers by journal count:

```sql
SELECT publisher, COUNT(*)
FROM journal
GROUP BY publisher
ORDER BY COUNT(*) DESC
LIMIT 25;
```

Top countries by number of journals:

```sql
SELECT  country,
        COUNT(*)
FROM journal
GROUP BY country
ORDER BY COUNT(*) DESC
LIMIT 10;
```

.. by number of papers:

```sql
SELECT  country,
        COUNT(*),
        SUM(release_count)
FROM journal
GROUP BY country
ORDER BY SUM(release_count) DESC
LIMIT 10;
```

Top languages by number of journals:

```sql
SELECT  lang,
        COUNT(*)
FROM journal
GROUP BY lang
ORDER BY COUNT(*) DESC
LIMIT 10;
```

... by number of papers:

```sql
SELECT  lang,
        COUNT(*),
        SUM(release_count)
FROM journal
GROUP BY lang
ORDER BY SUM(release_count) DESC
LIMIT 10;
```

## Fatcat Fulltext Coverage

Fulltext coverage by publisher type:

```sql
SELECT  publisher_type,
        AVG(ia_frac),
        AVG(preserved_frac),
        COUNT(*) AS journal_count,
        SUM(release_count) AS paper_count
FROM journal
GROUP BY publisher_type
ORDER BY SUM(release_count) DESC;
```

Top publishers with very little coverage:

```sql
SELECT  publisher,
        COUNT(*) AS journal_count,
        AVG(ia_frac)
FROM journal
WHERE ia_frac < 0.05
GROUP BY publisher
ORDER BY journal_count DESC
LIMIT 10;
```

Amount of fulltext by SHERPA/ROMEO journal color::

```sql
SELECT  sherpa_color,
        SUM(ia_count)
FROM journal
GROUP BY sherpa_color;
```

## Journal Homepages

Homepage URL counts:

```sql
SELECT COUNT(DISTINCT surt) as unique_urls, COUNT(DISTINCT issnl) as journals_with_hompages FROM homepage;
```

Journal counts by homepage status:

```sql
SELECT any_homepage, any_live_homepage, any_gwb_homepage, COUNT(*), ROUND(1.0 * COUNT(*) / (SELECT COUNT(*) FROM journal), 2) AS frac FROM journal GROUP BY any_homepage, any_live_homepage, any_gwb_homepage;
```

Number of unique journals that have a homepage pointing to wayback or archive.org:

```sql
SELECT COUNT(DISTINCT issnl) FROM homepage WHERE domain = 'archive.org';
```

Journals with the most homepage URLs:

```sql
SELECT  issnl,
        COUNT(*)
FROM homepage
GROUP BY issnl
ORDER BY COUNT(*) DESC
LIMIT 10;
```

Top/redundant URLs and SURTs:

```sql
SELECT  surt,
        COUNT(*)
FROM homepage
GROUP BY surt
ORDER BY COUNT(*) DESC
LIMIT 10;
```

What is the deal with all those "benjamins" URLs?

```sql
SELECT  publisher,
        name
FROM journal
LEFT JOIN homepage ON journal.issnl = homepage.issnl
WHERE homepage.surt = 'com,benjamins)/';
```

Domains that block us:

```sql
SELECT  domain,
        COUNT(*) as journal_homepages,
        SUM(blocked)
FROM homepage
GROUP BY domain
ORDER BY SUM(blocked) DESC
LIMIT 20;
```

Top duplicated domains:

```sql
SELECT  url,
        COUNT(*)
FROM homepage
GROUP BY url
ORDER BY COUNT(*) DESC
LIMIT 20;
```

Number of journals with a homepage that points to web.archive.org or archive.org:

```sql
SELECT COUNT(DISTINCT issnl)
FROM homepage
WHERE domain = 'archive.org';
```

Top publishers that have journals in wayback:

```sql
SELECT  publisher,
        COUNT(*)
FROM journal
LEFT JOIN homepage ON journal.issnl = homepage.issnl
WHERE homepage.domain = 'archive.org'
GROUP BY journal.publisher
ORDER BY COUNT(*) DESC
LIMIT 10;
```
Top publishers by number of journals missing a homepage:

```sql
SELECT  publisher,
        COUNT(*)
FROM journal
WHERE any_homepage=0
GROUP BY publisher
ORDER BY COUNT(*) DESC
LIMIT 20;
```

