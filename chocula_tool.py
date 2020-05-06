#!/usr/bin/env python3

"""
Count Chocula - online serials metadata and stats

  "one, two, three, un-preserved web-native open-access long-tail indie
  journals, hah, hah, hah!"

  (yeah, I know, this name isn't very good)
  (see also: https://teamyacht.com/ernstchoukula.com/Ernst-Choukula.html)

Commands:

    everything
    init_db
    summarize
    export
    export_fatcat

    index_doaj
    index_road
    index_crossref
    index_entrez
    index_norwegian
    index_szczepanski
    index_ezb
    index_wikidata
    index_openapc

    load_fatcat
    load_fatcat_stats

    export_urls
    update_url_status

Future commands:

    index_jurn
    index_datacite
    preserve_kbart --keeper SLUG
    preserve_sim

See TODO.md for more work-in-progress
"""

import sys
import csv
import argparse

from chocula import ChoculaDatabase
from chocula.config import *


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    parser.add_argument("--db-file",
        help="run in mode that considers only terminal HTML success",
        default='chocula.sqlite',
        type=str)
    parser.add_argument("--input-file",
        help="override default input file path",
        default=None,
        type=str)

    sub = subparsers.add_parser('everything',
        help="run all the commands")
    sub.set_defaults(func='everything')

    sub = subparsers.add_parser('init_db',
        help="create sqlite3 output file and tables")
    sub.set_defaults(func='init_db')

    sub = subparsers.add_parser('summarize',
        help="aggregate metadata from all tables into 'journals' table")
    sub.set_defaults(func='summarize')

    sub = subparsers.add_parser('export',
        help="dump JSON output")
    sub.set_defaults(func='export')

    sub = subparsers.add_parser('export_fatcat',
        help="dump JSON output in a format that can load into fatcat")
    sub.set_defaults(func='export_fatcat')

    # TODO: 'jurn'
    for ind in ('doaj', 'road', 'crossref', 'entrez', 'norwegian', 'szczepanski', 'ezb', 'gold_oa', 'wikidata', 'openapc'):
        sub = subparsers.add_parser('index_{}'.format(ind),
            help="load metadata from {}".format(ind))
        sub.set_defaults(func='index_{}'.format(ind))

    sub = subparsers.add_parser('load_fatcat',
        help="load fatcat container metadata")
    sub.set_defaults(func='load_fatcat')

    sub = subparsers.add_parser('load_fatcat_stats',
        help="update container-level stats from JSON file")
    sub.set_defaults(func='load_fatcat_stats')

    sub = subparsers.add_parser('export_urls',
        help="dump homepage URLs (eg, to crawl for status)")
    sub.set_defaults(func='export_urls')

    sub = subparsers.add_parser('update_url_status',
        help="import homepage URL crawl status")
    sub.set_defaults(func='update_url_status')

    args = parser.parse_args()
    if not args.__dict__.get("func"):
        print("tell me what to do! (try --help)")
        sys.exit(-1)

    cdb = ChoculaDatabase(args.db_file)
    if args.func.startswith('index_') or args.func in ('everything','summarize',):
        cdb.read_issn_map_file(ISSNL_FILE)
    func = getattr(cdb, args.func)
    func(args)

if __name__ == '__main__':
    main()

