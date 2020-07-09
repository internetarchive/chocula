
## Goal

For many long-tail journals, we have no known homepage. It is likely many of
these metadata records were actually never published, or are otherwise bad
metadata, but many are legitimate but simply missing metadata.

Want to rapidly skim though thousands of such journals and record homepage URLs
if they exist.

## Instructions

For each row in the spreadsheet, search the web or other sources for a journal
homepage. This should be an official, active site where new papers are
published, as well as historical papers.

The recommended workflow is to search for the ISSN-L and name in google, skim
the first page for likely hits, then click through to confirm that any hits are
actually journal sites. An easy way to do this is to check for the ISSN (or the
alternate "ISSNe" or "ISSNp") in the webpage itself; we will also check for
these identifiers in an automated manner to verify homepage matches. If there
do not seem to be any hits, mark the row as skipped and move on. You will
notice that many journals are published on platforms or using common software
like OJS (Open Journal Systems), Wordpress, or SciElo. If you notice this,
please tag in the `platform` column.

Generally are not interested in URLs to sites that are just indexing or listing
metadata about a journal, which often show up in search results. If it seems
like a journal has been retired, archived, or mirrored elsewhere, with all the
papers available, you can put such a URL in `other_url`. This is relatively
rare.

If the metadata (journal name) is aggregiously poor or mangled, and you find
the corrected canonical title, you can put that in the `corrected_title` column
(optional).

Recommend running through 25 random rows first without recording results to get
a feel for the process and ask any question.

Specific platforms we don't want any URLs from (not a complete list):

- issn.org
- sherpa.ac.uk
- any other lists of journal information
- wikidata.org
- scimago

Platforms which are ok to link to in the `other_url` column if no other hits:

- web.archive.org

Core columns to fill in for each row:

- `skipped` (yes or blank)
- `homepage_url`
- `platform` (eg, OJS, scielo, hypothesis, or blank)

Other columns that can be filled in, but aren't expecting them for most:

- `other_url`
- `corrected_title`
- `original_title` (non-English)
- `corrected_publisher`
- `inactive` (yes/no)
- `comment`

## Export Task List

Dump to TSV:

    .headers on
    .mode tabs
    .output chocula_missing_hompages_longtail.2020-05-05.tsv

    SELECT issnl, issnp, issne, name, publisher, country, lang, release_count
    FROM journal
    WHERE
        any_homepage=0
        AND has_dois=0
        AND is_longtail=1
        AND release_count < 10
        AND valid_issnl=1;

NOTE: this is a partial list, as of 2020-05-05 about 4600 rows, 

After the first round of manual homepage identification, as of 2020-07-08 there
are only 264 journals remaining selected by the above query.
