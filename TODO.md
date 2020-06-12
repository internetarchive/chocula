
priorities:
- coverage stats, particularly for longtail
- "still in print" flag
- clean out invalid ISSN-L from fatcat
- don't list dead URLs in fatcat

## Sources

- PKP OJS index
    => mostly redundant with DOAJ?
- dblp conferences/series
    => no container-only metadata dump available?
- MAG
- vanished journals
    => https://github.com/njahn82/vanished_journals
    => https://isaw.nyu.edu/publications/awol-index/
- sherpa/romeo refactor (no moreo updates)
- entrez refactor (no moreo updates)
- unpaywall journal-level classification
    => ask for journal-level dump or do munging
- SERP homepage munging
- repositories (?)
- jurn matches
- datacite metadata (?)
    => via munging
- currated quality lists (eg, national libraries)
    => https://www.arc.gov.au/excellence-research-australia
- public scopus list (?)
- scrape/munge public clarivate dumps
- "GOLD" importer (for scopus/WoS)
- ISSN metadata from portal.issn.org
    scraping is done
    only for ISSN-Ls from existing table
    https://portal.issn.org/resource/ISSN/1561-7645?format=json
    would require a good deal of munging (eg, MARC region -> ISO) (?)

improvements:
- entrez: "NLM Unique Id"
- JURN: finish 
- crossref: empty string identifiers?

## Code / Behavior

- black (syntax)
- log out index issues (duplicate ISSN-L, etc) to a file
- flag to delete old table/rows when loading (?)
- fully automated updates, cron, luigi/gluish style
    => downloads/uploads source metadata files
- check that all fields actually getting imported reasonably
- efficient fatcat export
    => filters for changes to make
    => not really necessary, fatcat importer already skips

## Schema

- `platform` column in database
- `container_type` column in database
    => munge this in various ways
    => if title is "blah,  Proceedings of the", set type to proceedings and re-write title
    => if title like "Workshop on", set type
- imprint/publisher distinction (publisher is big group)
- summary table should be superset of fatcat table
- `update_url_status` (needs re-write) (?)
