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
    export_urls

    directory <source>
        doaj
        road
        crossref
        entrez
        norwegian
        szczepanski
        ezb
        wikidata
        openapc
        sim

    load <source>
        fatcat_containers
        fatcat_stats
        homepage_status

    kbart <source>
        jstor
        clockss
        lockss
        portico

See TODO.md for more work-in-progress
"""

import sys
import csv
import argparse

from chocula import (
    ChoculaDatabase,
    ChoculaConfig,
    IssnDatabase,
    ALL_CHOCULA_DIR_CLASSES,
    ALL_CHOCULA_KBART_CLASSES,
)


def run_everything(config, database):

    database.init_db()
    for cls in ALL_CHOCULA_DIR_CLASSES:
        loader = cls(config)
        counts = loader.index_file(database)
        print(counts)
    for cls in ALL_CHOCULA_KBART_CLASSES:
        loader = cls(config)
        counts = loader.index_file(database)
        print(counts)

    database.load_fatcat_containers(config)
    database.load_fatcat_stats(config)
    database.load_homepage_status(config)
    database.summarize()
    print("### Done with everything!")


def run_directory(config, database, source):
    for cls in ALL_CHOCULA_DIR_CLASSES:
        if cls.source_slug == source:
            loader = cls(config)
            counts = loader.index_file(database)
            print(counts)
            return
    raise NotImplementedError(f"unknown source: {source}")


def run_kbart(config, database, source):
    for cls in ALL_CHOCULA_KBART_CLASSES:
        if cls.source_slug == source:
            loader = cls(config)
            counts = loader.index_file(database)
            print(counts)
            return
    raise NotImplementedError(f"unknown source: {source}")


def run_load(config, database, source):
    if source == "fatcat_stats":
        print(database.load_fatcat_stats(config))
    elif source == "fatcat_containers":
        print(database.load_fatcat_containers(config))
    elif source == "homepage_status":
        print(database.load_homepage_status(config))
    else:
        raise NotImplementedError(f"unknown source: {source}")


def main():
    parser = argparse.ArgumentParser(
        prog="python -m chocula", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers()

    parser.add_argument(
        "--db-file", help="sqlite database file", default="chocula.sqlite", type=str
    )

    sub = subparsers.add_parser("everything", help="run all the commands")
    sub.set_defaults(func="everything")

    sub = subparsers.add_parser("init_db", help="create sqlite3 output file and tables")
    sub.set_defaults(func="init_db")

    sub = subparsers.add_parser(
        "summarize", help="aggregate metadata from all tables into 'journals' table"
    )
    sub.set_defaults(func="summarize")

    sub = subparsers.add_parser("export", help="dump JSON output")
    sub.set_defaults(func="export")

    sub = subparsers.add_parser(
        "export_fatcat", help="dump JSON output in a format that can load into fatcat"
    )
    sub.set_defaults(func="export_fatcat")

    sub = subparsers.add_parser(
        "export_urls", help="dump homepage URLs (eg, to crawl for status)"
    )
    sub.set_defaults(func="export_urls")

    sub = subparsers.add_parser(
        "directory", help="index directory metadata from a given source"
    )
    sub.add_argument("source", type=str, help="short name of source to index")
    sub.set_defaults(func=run_directory)

    sub = subparsers.add_parser("load", help="load metadata of a given type")
    sub.add_argument("source", type=str, help="short name of source to index")
    sub.set_defaults(func=run_load)

    sub = subparsers.add_parser(
        "kbart", help="index KBART holding metadata for a given source"
    )
    sub.add_argument("source", type=str, help="short name of source to index")
    sub.set_defaults(func=run_kbart)

    args = parser.parse_args()
    if not args.__dict__.get("func"):
        parser.print_help()
        sys.exit(-1)

    config = ChoculaConfig.from_file()
    issn_db: Optional[IssnDatabase] = None
    if args.func in ("everything", "summarize", run_directory, run_kbart):
        issn_db = IssnDatabase(config.issnl.filepath)

    cdb = ChoculaDatabase(args.db_file, issn_db)
    if args.func == "everything":
        run_everything(config, cdb)
    elif args.func in (run_directory, run_load, run_kbart):
        args.func(config, cdb, args.source)
    else:
        # all other commands run on the ChoculaDatabase itself
        func = getattr(cdb, args.func)
        print(func(), file=sys.stderr)


if __name__ == "__main__":
    main()
