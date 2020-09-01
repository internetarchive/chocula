
## 2020-08-31

How big of a difference in preservation coverage stats does the inclusion of
PKP PLN numbers result in?

    select count(*), sum(journal.release_count), sum(journal.preserved_count) from journal join directory on journal.issnl = directory.issnl where directory.slug = 'pkp_pln';

    count(*)    sum(journal.release_count)  sum(journal.preserved_count)
    ----------  --------------------------  ----------------------------
    1356        343333                      283984                      

So about 60k releases.

## 2020-06-23

Where do back ISSN-Ls come from? Answer: exiting fatcat metadata.

    select count(*) from journal where valid_issnl = 0;
    => 4

    select count(*) from journal where known_issnl = 0;
    => 2304

    select directory.slug, count(*) from journal join directory on journal.issnl = directory.issnl where journal.known_issnl = 0 group by directory.slug order by count(*) desc limit 20;

    select count(*) from journal join fatcat_container on journal.issnl = fatcat_container.issnl where journal.known_issnl = 0;
    => 2,328
    => note: still a few dupe ISSN-L in fatcat_container


How many journals might be longtail but have just a handful of DOIs? And would
be lost if we filter by `has_doi=0`?

    select count(*) from journal where has_dois = 1 and release_count <= 10;
    9054

    select count(*) from journal where has_dois = 1 and is_longtail = 1;
    15,575

    select count(*) from journal where has_dois = 1 and (is_active is null or is_active = 1) and release_count <= 10 and any_homepage = 1;
    => 5,843

How many *journals* would old query turn up? NOTE: have not verified new homepage URLs

    SELECT COUNT(DISTINCT journal.issnl), COUNT(DISTINCT homepage.url)
    FROM homepage
    LEFT JOIN journal ON homepage.issnl = journal.issnl
    WHERE
        homepage.terminal_status_code = 200
        AND journal.is_longtail = 1
        AND homepage.domain != 'archive.org'
        AND homepage.host NOT LIKE '%scielo%'
        AND homepage.domain != 'jst.go.jp'
        AND homepage.host != 'books.google.com'
        AND homepage.host != 'www.google.com'
        AND journal.has_dois = 0;
    => 16,471 journals
    => 19,460 URLs

New tweaks:

    SELECT COUNT(DISTINCT journal.issnl), COUNT(DISTINCT homepage.url)
    FROM homepage
    LEFT JOIN journal ON homepage.issnl = journal.issnl
    WHERE
        (homepage.terminal_status_code = 200 or homepage.blocked or homepage.terminal_status_code is null)
        AND homepage.domain != 'archive.org'
        AND homepage.host NOT LIKE '%scielo%'
        AND homepage.domain != 'jst.go.jp'
        AND homepage.host != 'books.google.com'
        AND homepage.host != 'www.google.com'
        AND homepage.domain != 'oclc.org'
        AND homepage.host != 'www.ncbi.nlm.nih.gov'
        AND homepage.domain != 'umi.com'
        AND homepage.domain != 'doi.org'
        AND homepage.host != 'www.thefreelibrary.com'
        AND (journal.is_longtail = 1
            OR journal.publisher_type = 'society'
            OR journal.publisher_type = 'unipress' 
            OR journal.publisher_type IS NULL)
        AND (journal.has_dois = 0 or journal.release_count < 20);
    => 57,637 journals
    => 70,770 homepages

This is a significant increase in size over previous crawls!

