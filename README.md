
Chocula is a python script to parse and merge journal-level metadata from
various sources into a consistent sqlite3 database file for analysis.

## Quickstart

You need `python3`, `pipenv`, and `sqlite3` installed.

First fetch datasets:

    cd data
    ./fetch.sh
    cd ..

Then re-generate entire sqlite3 database from scratch:

    pipenv shell
    ./chocula.py everything

Now you can explore the database; see `chocula_schema.sql` for the output schema.

    sqlite3 chocula.sqlite

## History / Name

This is the 3rd or 4th iteration of open access journal metadata munging as
part of the fatcat project; earlier attempts were crude ISSN spreadsheet
munging, then the `oa-journals-analysis` repo (Jupyter notebook and a web
interface), then the `fatcat:extra/journal_metadata/` script for bootstrapping
fatcat container metadata. This repo started as the fatcat `journal_metadata`
directory and retains the git history of that folder.

The name "chocula" comes from a half-baked pun on Count Chocula... something
something counting, serials, cereal.
[Read more about Count Chocula](https://teamyacht.com/ernstchoukula.com/Ernst-Choukula.html).


## ISSN-L Munging

Unfortunately, there seem to be plenty of legitimate ISSNs that don't end up in
the ISSN-L table. On the portal.issn.org public site, these are listed as:

    "This provisional record has been produced before publication of the
    resource.  The published resource has not yet been checked by the ISSN
    Network.It is only available to subscribing users."

For example:

- 2199-3246/2199-3254: Digital Experiences in Mathematics Education

Previously these were allowed through into fatcat, so some 2000+ entries exist.
This allowed through at least 110 totally bogus ISSNs. Currently, chocula
filters out "unknown" ISSN-Ls unless they are coming from existing fatcat
entities.


## Sources

The `./data/fetch.sh` script will fetch mirrored snapshots of all these
datasets.

A few sources of normalization/mappings:

- ISSN-L (from ISSN org)
    - Original: <https://www.issn.org/wp-content/uploads/2014/03/issnltables.zip>
    - Snapshot: <https://archive.org/download/issn_issnl_mappings/20180216.ISSN-to-ISSN-L.txt>
- ISO 639-1 language codes: https://datahub.io/core/language-codes
- ISO 3166-1 alpha-2 country codes

In order of precedence (first higher than later):

- NCBI Entrez (Pubmed)
    - Original: <ftp://ftp.ncbi.nlm.nih.gov/pubmed/J_Entrez.txt>
    - Snapshot: <https://archive.org/download/ncbi-entrez-2019/J_Entrez.txt>
- DOAJ
    - Original: <https://doaj.org/csv>
    - Snapshot: <https://archive.org/download/doaj_bulk_metadata_2019/doaj_20190124.csv>
- ROAD
    - Original: <http://road.issn.org/en/contenu/download-road-records>
    - Snapshot: <https://archive.org/download/road-issn-2018/2018-01-24/export-issn.zip>
- SHERPA/ROMEO
    - Original: <http://www.sherpa.ac.uk/downloads/journal-title-issn-urls.php> (requires reg)
    - Mirror: <http://www.moreo.info/?csv=romeo-journals.csv>
    - Snapshot:
- Norwegian Registry
    - Original: <https://dbh.nsd.uib.no/publiseringskanaler/AlltidFerskListe>
    - Snapshot: <https://archive.org/download/norwegian_register_journals>
- Wikidata via SPARQL Query
    - SPARQL: <https://archive.org/download/wikidata-journal-metadata/wikidata.sparql>
    - Snapshot: <https://archive.org/download/wikidata-journal-metadata>
- KBART reports: LOCKSS, CLOCKSS, Portico
    - Original: (multiple, see README in IA item)
    - Snapshot: <https://archive.org/download/keepers_reports_201912>
- JSTOR
    - Original: <https://support.jstor.org/hc/en-us/articles/115007466248-JSTOR-title-lists>
- Crossref title list (not DOIs)
    - Original: <https://wwwold.crossref.org/titlelist/titleFile.csv>
    - Snapshot: <https://archive.org/download/crossref_doi_titles>
- OpenAPC Dataset
    - Original: <https://github.com/OpenAPC/openapc-de/blob/master/data/apc_de.csv>
    - Snapshot: <https://archive.org/download/openapc-dataset>
- EZB Metadata
    - Snapshot: <https://archive.org/download/ezb_snapshot_2019-07-11>
- IA SIM Microfilm catalog
    - Original: <https://archive.org/download/SerialsOnMicrofilmCollection/MASTER%20TITLE_METADATA_LIST_20171019.xlsx>
- IA homepage crawl attempts

The SHERPA/ROMEO content comes from the list helpfully munged by moreo.info.
UPDATE: this site is now defunct (404).

General form here is to build a huge python dict in memory, keyed by the
ISSN-L, then write out to disk as JSON. Then the journal-metadata importer
takes a subset of fields and inserts to fatcat. Lastly, the elasticsearch
transformer takes a subset/combination of 

## Fatcat Container Counts

Generate a list of ISSN-L identifiers, fetch each from fatcat web peudo-API, and write to JSON.

    cat container_export.json | jq .issnl -r | sort -u > container_issnl.tsv
    cat container_issnl.tsv | parallel -j10 curl -s 'https://fatcat.wiki/container/issnl/{}/stats.json' | jq -c . > container_stats.json

Then load in to chocula and recaculate stats:

    pipenv shell
    ./chocula.py load_fatcat_stats container_stats.json
    ./chocula.py summarize

    # also, upload stats to an IA item, update fetch.sh and chocula.py variables

## Journal Homepage Crawl Status

The `check_issn_urls.py` script tries crawling journal homepages to see if they
are "live" on the web. To regenerate these stats:

    # assuming you have a fresh database
    pipenv shell
    ./chocula.py export_urls | shuf > urls_to_crawl.tsv
    parallel -j10 --bar --pipepart -a urls_to_crawl.shuf.tsv ./check_issn_urls.py > url_status.json
    ./chocula.py update_url_status url_status.json
    ./chocula.py summarize

Might also want to upload results at this point.

