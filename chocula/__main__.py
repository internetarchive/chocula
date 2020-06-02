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
    index_sim

    load_fatcat_containers
    load_fatcat_stats
    load_homepage_status

    export_urls

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

from chocula import ChoculaDatabase, ChoculaConfig, IssnDatabase, ALL_CHOCULA_DIR_CLASSES


def run_everything(config, database):

    database.init_db()
    for cls in ALL_CHOCULA_DIR_CLASSES:
        loader = cls(config)
        counts = loader.index_file(database)
        print(counts)

    # XXX: TODO:
    database.load_fatcat_containers(config)
    database.load_fatcat_stats(config)
    # XXX: TODO:
    #self.preserve_kbart('lockss', LOCKSS_FILE)
    #self.preserve_kbart('clockss', CLOCKSS_FILE)
    #self.preserve_kbart('portico', PORTICO_FILE)
    #self.preserve_kbart('jstor', JSTOR_FILE)
    #self.preserve_sim(args)
    database.load_homepage_status(config)
    database.summarize()
    print("### Done with everything!")

def run_index(config, database, cls):
    loader = cls(config)
    counts = loader.index_file(database)
    print(counts)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    parser.add_argument("--db-file",
        help="sqlite database file",
        default='chocula.sqlite',
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

    for cls in ALL_CHOCULA_DIR_CLASSES:
        sub = subparsers.add_parser('index_{}'.format(cls.source_slug),
            help="load metadata from {}".format(cls.source_slug))
        sub.set_defaults(func='index_{}'.format(cls.source_slug), index_cls=cls)

    sub = subparsers.add_parser('load_fatcat_containers',
        help="load fatcat container metadata")
    sub.set_defaults(func='load_fatcat_containers')

    sub = subparsers.add_parser('load_fatcat_stats',
        help="update container-level stats from JSON file")
    sub.set_defaults(func='load_fatcat_stats')

    sub = subparsers.add_parser('export_urls',
        help="dump homepage URLs (eg, to crawl for status)")
    sub.set_defaults(func='export_urls')

    sub = subparsers.add_parser('load_homepage_status',
        help="import homepage URL crawl status")
    sub.set_defaults(func='load_homepage_status')

    args = parser.parse_args()
    if not args.__dict__.get("func"):
        print("tell me what to do! (try --help)")
        sys.exit(-1)

    config = ChoculaConfig.from_file()
    if args.func.startswith('index_') or args.func in ('everything','summarize',):
        issn_db = IssnDatabase(config.issnl.filepath)
    else:
        issn_db = None
    cdb = ChoculaDatabase(args.db_file, issn_db)
    if args.func == 'everything':
        run_everything(config, cdb)
    elif args.func.startswith('index_'):
        print(run_index(config, cdb, args.index_cls))
    elif args.func.startswith('load_'):
        func = getattr(cdb, args.func)
        print(func(config))
    else:
        func = getattr(cdb, args.func)
        print(func(), file=sys.stderr)

if __name__ == '__main__':
    main()

