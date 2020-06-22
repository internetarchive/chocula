
Chocula: Scholary Journal Metadata Munging
==========================================

<div align="center">
<img src="extra/count_chocola.jpg">
</div>

**Chocula** is a python tool for parsing and merging journal-level metadata
from various sources into a sqlite3 database file for analysis. It is currently
the main source of journal-level metadata for the [fatcat](https://fatcat.wiki)
catalog of published papers.

## Quickstart

You need `python3.7`, `pipenv`, and `sqlite3` installed. Commands are run via
`make`. If you don't have `python3.7` installed system-wide, try installing
`pyenv`.

Set up dependencies and fetch source metadata:

    make dep fetch-sources

Then re-generate entire sqlite3 database from scratch:

    make database

Now you can explore the database; see `chocula_schema.sql` for the output schema.

    sqlite3 chocula.sqlite

## Developing

There is partial test coverage, and we verify python type annotations. Run the
tests with:

    make test

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


## Source Metadata

The `sources.toml` configuration file contains a canoncial list of metadata
files, the last time they were updated, and original URLs for mirrored files.
The general workflow is that all metadata files are bunled into "source
snapshots" and uploaded/downloaded from the Internet Archive (archive.org)
together.

There is some tooling (`make update-sources`) to automatically download fresh
copies of some files. Others need to be fetched manually. In all cases, new
files are not automatically integrated: they are added to a sub-folder of
`./data/` and must be manually copied and `sources.toml` updated with the
appropriate date before they will be used.

Some sources of metadata were helpfully pre-parsed by the maintainer of
<https://moreo.info>. Unfortunately this site is now defunct and the metadata
is out of date.

Adding new directories or KBART preservation providers is relatively easy, by
creating new helpers in `chocula/directories/` and/or `chocula/kbart.py`.

## Updating Homepage Status and Countainer Counts

Run these commands from a fast connection; they will run with parallel
processes. These hit only public URLs and API
endpoints, but you would probably have the best luck running these from inside
the Internet Archive cluster IP space:

    make data/2020-06-03/homepage_status.json
    make data/2020-06-03/container_stats.json

Then copy these files to `data/` (no sub-directory) and update the dates in
`sources.toml`. Update the sqlite database with:

    pipenv run python -m chocula load_fatcat_stats
    pipenv run python -m chocula load_homepage_status
    pipenv run python -m chocula summarize

