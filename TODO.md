
2020-05-06
x python3.7
x type annotations / dataclasses
x "update-sources"
    => makefile
- run "everything" successfully
- "upload-sources"
    => to archive.org, with datetime
- "fetch-sources"
    => all snapshots in a single ia item, with datetime
- scielo journal metadata
- kbart loading
- "platform" column in database
- rewrite README

- flag to delete old table/rows when loading (?)
- "loaders" not directories?
- makefile
- black
- refactor most code into module directory
- tests
    => index process
- update upstreams

refactors:
- "directory" command with directory as arg
- "kbart" command with directory as arg
- "load" command with directory as arg

https://isaw.nyu.edu/publications/awol-index/

## Chocula

- fully automated updates, luigi/gluish style
    => downloads/uploads source metadata files
    => outputs config file for chocula run
    => runs chocula everything

priorities:
- coverage stats, particularly for longtail
- "still in print" flag
- clean out invalid ISSN-L from fatcat
- don't list dead URLs in fatcat
- summary report of some of above
- when updating fatcat:
    if title is "blah,  Proceedings of the", set type to proceedings and re-write title
    if title like "Workshop on", set type

source improvements:
- entrez: "NLM Unique Id"
- JURN: finish 
- crossref: empty string identifiers?
- scielo: https://scielo.org/en/journals/list-by-alphabetical-order/?export=csv
- https://www.arc.gov.au/excellence-research-australia (journal list)

- public scopus list (?)
- scrape/munge public clarivate dumps
- import JURN into fatcat (one way or another)
    => try to title match and get ISSN-L
    => manual lookups for remainders?
- "GOLD" importer (for scopus/WoS)
- check that all fields actually getting imported reasonably

- could poll portal.issn.org like:
    https://portal.issn.org/resource/ISSN/1561-7645?format=json
    would require a good deal of munging (eg, MARC region -> ISO)
- KBART imports (with JSON, so only a single row per slug)
- imprint/publisher distinction (publisher is big group)
- summary table should be superset of fatcat table
- add timestamp columns to enable updates?
- fatcat export (filters for changes to make, writes out as JSON)
- update_url_status (needs re-write)
- log out index issues (duplicate ISSN-L, etc) to a file
- validate against GOLD OA list

