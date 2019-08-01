
## Chocula

priorities:
x fraction/which are pointing to wayback
- coverage stats, particularly for longtail
x wikidata linkage (prep for wikimania)
- "still in print" flag
- clean out invalid ISSN-L from fatcat
- don't list dead URLs in fatcat
- summary report of some of above
- update all fatcat (wikidata QID, urls, fixed ISSN-L, etc)


- public scopus list (?)
- scrape/munge public clarivate dumps
- import JURN into fatcat (one way or another)
    => try to title match and get ISSN-L
    => manual lookups for remainders?
- dump json
- "GOLD" importer (for scopus/WoS)
- check that all fields actually getting imported reasonably
- homepage crawl/status script

- KBART imports (with JSON, so only a single row per slug)
- imprint/publisher distinction (publisher is big group)
- summary table should be superset of fatcat table
- add timestamp columns to enable updates?
- fatcat export (filters for changes to make, writes out as JSON)
- update_url_status (needs re-write)
- index -> directory
- log out index issues (duplicate ISSN-L, etc) to a file
- validate against GOLD OA list
- decide what to do with JURN... match? fuzzy match? create missing fatcat?
- lots of bogus ISSN-L, like 9999-9999 or 0000-0000. should both validate
  check digit and require an ISSN-L to actually exist.

