
KBART registry:
- https://sites.google.com/site/kbartregistry/
- Project Muse as a Keeper?

why did ISSN-L list have bad single line (1300-350X)?

x wikidata update
x SIM max-year limit
- handle no-issn dblp containers (?)
- new DOAJ csv schema
- ROAD update
- include vanished status as a flag/tag ("status"?)

priorities:
- coverage stats, particularly for longtail
- `is_active` coverage
- clean out invalid ISSN-L from fatcat
- don't list dead URLs in fatcat
- SIM missing/bad ISSNs
    Counter({'total': 14860, 'inserted': 11421, 'missing-issn': 2863, 'no-match': 555, 'duplicate': 21})
- publisher KBART
    springer: http://adminportal.springernature.com/metadata/kbart
    taylor&francis: https://www.tandfonline.com/page/title-lists
        also "ceased" list
    elsevier: https://www.elsevier.com/solutions/sciencedirect/content/journal-title-lists
    sage: https://us.sagepub.com/en-us/nam/title-lists
    oup: https://global.oup.com/academic/librarians/manage/kbart-files/?cc=us&lang=en&
    https://www.annualreviews.org/page/librarians/metadata/titlelists
    https://iopscience.iop.org/bookListInfo/title-lists
    https://support.gale.com/tlist/products/
        https://titlelist.gale.com/titlelist/
    IEEE: https://ieeexplore.ieee.org/Xplorehelp/administrators-and-librarians/title-lists#kbart-phase-ii-compliant-title-lists
    ACM: https://dl.acm.org/about/content


## Sources

- EBSCO title lists: https://www.ebsco.com/title-lists
- government lists
    => india: University Grants Commission (UGC-CARE, group I)
        https://ugccare.unipune.ac.in/apps1/home/index
    => indonesia list?
    => ERIH PLUS
        https://dbh.nsd.uib.no/publiseringskanaler/erihplus/
    => "CORE" (australia? not core.ac.uk)
- preservation coverage
    => National Digital Preservation Program, China
    => Library of Congress
- additional hathitrust (many more ISSNs/journals)
- unpaywall journal-level classification (OA color)
    => ask for journal-level dump or do munging
- jurn matches
    => somebody on github did an openrefine match
- public scopus list (?)
- scrape/munge public clarivate dumps
- repositories (?)
- datacite metadata (?)
    => via munging
- dblp conferences/series
    => no container-only metadata dump available?
- SERP homepage munging
- currated quality lists (eg, national libraries)
- "GOLD" importer (for scopus/WoS)
- PKP OJS index
    => mostly redundant with DOAJ?

improvements:
- sherpa/romeo refactor (no moreo updates)
- entrez refactor (no moreo updates)
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

- `original_name`
- `platform` column in database
- `container_type` column in database
    => munge this in various ways
    => if title is "blah,  Proceedings of the", set type to proceedings and re-write title
    => if title like "Workshop on", set type
- imprint/publisher distinction (publisher is big group)
- summary table should be superset of fatcat table
- `update_url_status` (needs re-write) (?)
