
from __future__ import annotations

import sys
import csv
import json
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

import urlcanon
import surt
import tldextract
import ftfy
import stdnum.issn

from chocula.util import *


@dataclass
class HomepageUrl:
    url: str
    surt: str
    host: Optional[str]
    domain: Optional[str]
    suffix: Optional[str]

    def to_db_tuple(self, issnl: str) -> Tuple:
        """
        Relevant columns are:

            issnl TEXT NOT NULL,
            surt TEXT NOT NULL,
            url TEXT NOT NULL,
            host TEXT,
            domain TEXT,
            suffix TEXT,

        Returns a tuple in that order for inserting.
        """
        return (issnl, self.surt, self.url, self.host, self.domain, self.suffix)

    @classmethod
    def from_url(cls, url: str) -> Optional[HomepageUrl]:
        """
        Returns None if url is really bad (not a URL).
        """
        if not url or 'mailto:' in url.lower() or url.lower() in ('http://n/a', 'http://na/', 'http://na'):
            return None
        if url.startswith('www.'):
            url = "http://" + url
        if url.startswith('ttp://') or url.startswith('ttps://'):
            url = "h" + url
        url.replace('Http://', 'http://')

        url = str(urlcanon.semantic_precise(url))
        if url == 'http://na/':
            # sort of redundant with above, but some only match after canonicalization
            return None
        url_surt = surt.surt(url)
        tld = tldextract.extract(url)
        host = '.'.join(tld)
        if host.startswith('.'):
            host = host[1:]
        return HomepageUrl(url=url,
                    surt=url_surt,
                    host=host,
                    domain=tld.registered_domain,
                    suffix=tld.suffix)

def test_from_url():
    
    assert HomepageUrl.from_url("http://thing.core.ac.uk").domain == 'core.ac.uk'
    assert HomepageUrl.from_url("http://thing.core.ac.uk").host == 'thing.core.ac.uk'
    assert HomepageUrl.from_url("http://thing.core.ac.uk").suffix== 'ac.uk'

    assert HomepageUrl.from_url("google.com").suffix == 'com'
    assert HomepageUrl.from_url("google.com").host == 'google.com'

    assert HomepageUrl.from_url("mailto:bnewbold@bogus.com") == None
    assert HomepageUrl.from_url("thing.com").url == 'http://thing.com/'
    assert HomepageUrl.from_url("Http://thing.com///").url == 'http://thing.com/'

@dataclass
class UrlCrawlStatus:
    status_code: Optional[int]
    crawl_error: Optional[str]
    terminal_url: Optional[str]
    terminal_status_code: Optional[int]
    platform_software: Optional[str]
    issnl_in_body: Optional[bool]
    blocked: Optional[bool]
    gwb_url_success_dt: Optional[str]
    gwb_terminal_url_success_dt: Optional[str]

@dataclass
class DirectoryInfo:
    directory_slug: str
    raw_issn: Optional[str] = None
    issnl: Optional[str] = None
    issne: Optional[str] = None
    issnp: Optional[str] = None
    custom_id: Optional[str] = None
    name: Optional[str] = None
    original_name: Optional[str] = None
    publisher: Optional[str] = None
    abbrev: Optional[str] = None
    platform: Optional[str] = None
    country: Optional[str] = None
    langs: List[str] = field(default_factory=list)
    homepage_urls: List[HomepageUrl] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def to_db_tuple(self) -> Tuple:
        """
        Actual database schema is:

            issnl TEXT NOT NULL,
            slug TEXT NOT NULL,
            identifier TEXT,
            name TEXT,
            extra TEXT,
        
        Returns a tuple in that order.
        """
        if not self.issnl:
            raise ValueError
        extra_dict  = self.extra

        for k in ('issne', 'issnp', 'name', 'publisher', 'abbrev', 'platform',
                  'country', 'langs', 'original_name'):
            if self.__dict__[k]:
                extra_dict[k] = self.__dict__[k]

        extra_str: Optional[str] = None
        if extra_dict:
            extra_str = json.dumps(extra_dict, sort_keys=True)

        return (
            self.issnl,
            self.directory_slug,
            self.custom_id or None,
            self.name or None,
            extra_str,
        )

    @classmethod
    def from_db(cls):
        raise NotImplementedError()


class IssnDatabase():
    """
    Holds complete ISSN/ISSN-L table and helps with lookups and munging of raw
    ISSN strings
    """

    def __init__(self, issn_issnl_file_path: str):
        self.issn_issnl_map: Dict[str, str] = dict()
        self.read_issn_map_file(issn_issnl_file_path)

    def read_issn_map_file(self, issn_map_path: str):
        print("##### Loading ISSN-L map file...", file=sys.stderr)
        with open(issn_map_path, 'r') as issn_map_file:
            for line in issn_map_file:
                if line.startswith("ISSN") or len(line) == 0:
                    continue
                (issn, issnl) = line.split()[0:2]
                self.issn_issnl_map[issn] = issnl
                # double mapping makes lookups easy
                if not issnl in self.issn_issnl_map:
                    self.issn_issnl_map[issnl] = issnl
        count = len(self.issn_issnl_map)
        print(f"Got {count} ISSN-L mappings", file=sys.stderr)

    def issn2issnl(self, issn: str) -> Optional[str]:
        return self.issn_issnl_map.get(issn)

    def munge_issns(self, info: DirectoryInfo) -> DirectoryInfo:
        """
        Cleans up the ISSN fields of a DirectoryInfo object, and tries to
        lookup or confirm an ISSN-L mapping.

        Note that if the passed ISSN-L number is not in the ISSN-L directory,
        it will be wiped from the returned info object.

        TODO: check what previous behavior was... passing through raw_issn?
        """

        if info.issnl:
            info.issnl = clean_issn(info.issnl)
        if info.raw_issn:
            info.raw_issn = clean_issn(info.raw_issn)
        if info.issne:
            info.issne = clean_issn(info.issne)
        if info.issnp:
            info.issnp = clean_issn(info.issnp)

        issnl = None
        for lookup in (info.issnl, info.raw_issn, info.issne, info.issnp):
            if not lookup:
                continue
            issnl = self.issn2issnl(lookup)
            if issnl:
                break
        info.issnl = issnl
        return info


class ChoculaDatabase():
    """
    Wraps a sqlite3 database
    """

    def __init__(self, db_file, issn_db):
        """
        To create a temporary database, pass ":memory:" as db_file
        """
        self.db = sqlite3.connect(db_file, isolation_level='EXCLUSIVE')
        self.data = dict()
        self.issn_db = issn_db

    def insert_directory(self, info: DirectoryInfo, cur: Any = None) -> str:
        """
        This method does some general cleanup on a directory info object (eg,
        munges ISSNs), then inserts into the database.

        Also inserts any/all nested homepage URLs.

        Returns status of insert, which could be:

        - inserted
        - duplicate
        - missing-issn
        - no-match
        """

        info = self.issn_db.munge_issns(info)
        if not (info.issnl or info.raw_issn or info.issne or info.issnp):
            return "missing-issn"
        if not info.issnl:
            return "no-match"

        if not cur:
            cur = self.db.cursor()

        try:
            cur.execute("INSERT INTO directory VALUES (?,?,?,?,?)",
                info.to_db_tuple())
        except sqlite3.IntegrityError as ie:
            if str(ie).startswith("UNIQUE"):
                return "duplicate"
            raise ie

        for url in info.homepage_urls:
            self.insert_homepage(info.issnl, url, cur)

        return "inserted"

    def insert_homepage(self, issnl: str, homepage: HomepageUrl, cur: Any) -> str:

        try:
            cur.execute(
                "INSERT OR REPLACE INTO homepage (issnl, surt, url, host, domain, suffix) VALUES (?,?,?,?,?,?)",
                homepage.to_db_tuple(issnl))
        except sqlite3.IntegrityError as ie:
            if str(ie).startswith("UNIQUE"):
                return "duplicate"
            raise ie

        return "inserted"

    def parse_kbart(self, name, path):
        """
        Transforms a KBART file into a dict of dicts; but basically a list of
        JSON objects, one per journal. KBART files can have multiple rows per
        journal (eg, different year spans), which is why this pass is needed.
        """
        print("##### Parsing KBART file for {}...".format(name))
        #publication_title      print_identifier        online_identifier       date_first_issue_online num_first_vol_online    num_first_issue_online  date_last_issue_online  num_last_vol_online     num_last_issue_online   title_url       first_author    title_id        embargo_info    coverage_depth  coverage_notes  publisher_name
        kbart_dict = dict()
        raw_file = open(path, 'rb').read().decode(errors='replace')
        fixed_file = ftfy.fix_text(raw_file)
        reader = csv.DictReader(fixed_file.split('\n'), delimiter='\t')
        counts = Counter()
        for row in reader:
            if not row['print_identifier'] and not row['online_identifier']:
                counts['no-issn'] += 1
                continue
            issnl, status = self.lookup_issnl(
                issnp=row['print_identifier'],
                issne=row['online_identifier'],
            )
            counts[status] += 1
            if not issnl:
                continue

            info = dict(
                title=row['publication_title'] or None,
                publisher=row['publisher_name'] or None,
                url=row['title_url'] or None,
                embargo_info=row['embargo_info'] or None,
            )

            d = kbart_dict.get(issnl, info)

            old_spans = d.get('year_spans', [])
            if row['date_first_issue_online'] and row['date_last_issue_online']:
                start = int(row['date_first_issue_online'][:4])
                end = int(row['date_last_issue_online'][:4])
                if not start <= end:
                    print("{}: {} not before {}! er, mangling".format(
                        issnl,
                        row['date_first_issue_online'],
                        row['date_last_issue_online']))
                    new_spans = [[end, start]]
                else:
                    new_spans = [[start, end]]
                d['year_spans'] = merge_spans(old_spans, new_spans)
        print(counts)
        return kbart_dict


    def index_sim(self, args):
        path = args.input_file or SIM_FILE
        print("##### Loading SIM Metadata...")
        #NA Pub Cat ID,Title,Publisher,ISSN,Impact Rank,Total Cities,Journal Impact Factor,Eigenfact or Score,First Volume,Last Volume,NA Gaps,"Scholarly / Peer-\n Reviewed","Peer-\n Reviewed",Pub Type,Pub Language,Subjects
        reader = csv.DictReader(open(path))
        counts = Counter()
        cur = self.db.cursor()
        for row in reader:
            if not row['ISSN'] or row['ISSN'] == "NULL":
                counts['no-issn'] += 1
                continue
            issnl, status = self.add_issn(
                'ia_sim',
                raw_issn=row['ISSN'][:9],
                name=row['Title'],
                publisher=row['Publisher'],
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            d = self.data[issnl]
            sim = dict()
            sim['id'] = row['NA Pub Cat ID']
            first_year = row['First Volume']
            if first_year:
                first_year = int(first_year)
                sim['first_year'] = int(row['First Volume'])
            else:
                first_year = None
            last_year = row['Last Volume']
            if last_year:
                last_year = int(last_year)
                sim['last_year'] = last_year
            else:
                last_year = None
            gaps = [int(g) for g in row['NA Gaps'].split(';') if g.strip()]
            if gaps:
                sim['gaps'] = gaps
            if first_year and last_year:
                sim['year_spans'] = gaps_to_spans(first_year, last_year, gaps)
            if row['Pub Language']:
                self.add_lang(issnl, row['Pub Language'])
            # TODO: 'Pub Type'
            all_keys = list(sim.keys())
            for k in all_keys:
                if not sim[k]:
                    sim.pop(k)
            self.data[issnl]['sim'] = sim
        cur.close()
        self.db.commit()
        print(counts)

    def update_url_status(self, args):
        path = args.input_file or IA_CRAWL_FILE
        print("##### Loading IA Homepage Crawl Results...")
        counts = Counter()
        cur = self.db.cursor()
        for row in open(path, 'r'):
            if not row.strip():
                continue
            row = json.loads(row)
            counts['total'] += 1
            url = row['url']
            assert(url)
            if row.get('gwb_url_success_dt') == 'error':
                row['gwb_url_success_dt'] = None
            if row.get('gwb_terminal_url_success_dt') == 'error':
                row['gwb_terminal_url_success_dt'] = None
            cur.execute("UPDATE homepage SET status_code=?, crawl_error=?, terminal_url=?, terminal_status_code=?, platform_software=?, issnl_in_body=?, blocked=?, gwb_url_success_dt=?, gwb_terminal_url_success_dt=? WHERE url=?",
                (row['status_code'],
                 row.get('crawl_error'),
                 row.get('terminal_url'),
                 row.get('terminal_status_code'),
                 row.get('platform_software'),
                 row.get('issnl_in_body'),
                 row.get('blocked'),
                 row.get('gwb_url_success_dt'),
                 row.get('gwb_terminal_url_success_dt'),
                 url))
            counts['updated'] += 1
        cur.close()
        self.db.commit()
        print(counts)

    def load_fatcat(self, args):
        path = args.input_file or FATCAT_CONTAINER_FILE
        print("##### Loading Fatcat Container Entities...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        cur = self.db.cursor()
        for row in json_file:
            if not row:
                continue
            row = json.loads(row)
            if row['state'] != 'active':
                continue
            counts['total'] += 1
            extra = row.get('extra', dict())
            issne = extra.get('issne')
            issnp = extra.get('issnp')
            country = extra.get('country')
            languages = extra.get('languages', [])
            lang = None
            if languages:
                lang = languages[0]
            try:
                cur.execute("INSERT OR REPLACE INTO fatcat_container (issnl, ident, revision, issne, issnp, wikidata_qid, name, container_type, publisher, country, lang) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (row.get('issnl'),
                     row['ident'],
                     row['revision'],
                     issne,
                     issnp,
                     row.get('wikidata_qid'),
                     row['name'],
                     row.get('container_type'),
                     extra.get('publisher'),
                     country,
                     lang,
                    ))
            except sqlite3.IntegrityError as ie:
                if str(ie).startswith("UNIQUE"):
                    return None, "duplicate-issnl"
                raise ie
            counts['inserted'] += 1
            if row.get('issnl'):
                urls = extra.get('urls', [])
                for url in urls:
                    self.add_url(row['issnl'], url)
        cur.close()
        self.db.commit()
        print(counts)

    def load_fatcat_stats(self, args):
        path = args.input_file or FATCAT_STATS_FILE
        print("##### Loading Fatcat Container Stats...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        cur = self.db.cursor()
        for row in json_file:
            if not row:
                continue
            row = json.loads(row)
            total = int(row['total'])
            if total > 0:
                ia_frac = float(row['in_web'])/total
                preserved_frac = float(row['is_preserved'])/total
            else:
                ia_frac = None
                preserved_frac = None
            cur.execute("UPDATE fatcat_container SET release_count = ?, ia_count = ?, ia_frac = ?, preserved_count = ?, preserved_frac = ? WHERE issnl = ?",
                (total, row['in_web'], ia_frac, row['is_preserved'], preserved_frac, row['issnl']))
            counts['updated'] += 1
        cur.close()
        self.db.commit()
        print(counts)

    def export_urls(self, args):
        cur = self.db.cursor()
        self.db.row_factory = sqlite3.Row
        cur = self.db.execute("SELECT issnl, url FROM homepage;")
        for hrow in cur:
            assert(hrow['url'])
            assert(len(hrow['url'].split()) == 1)
            print('\t'.join((hrow['issnl'], hrow['url'])))

    def summarize(self, args):
        print("##### Summarizing Everything...")
        counts = Counter()
        cur = self.db.cursor()
        self.db.row_factory = sqlite3.Row
        index_issnls = list(cur.execute('SELECT DISTINCT issnl FROM directory'))
        fatcat_issnls = list(cur.execute('SELECT DISTINCT issnl FROM fatcat_container WHERE issnl IS NOT null'))
        all_issnls = set([i[0] for i in index_issnls + fatcat_issnls])
        print("{} total ISSN-Ls".format(len(all_issnls)))
        for issnl in list(all_issnls):
            #print(issnl)
            counts['total'] += 1

            out = dict()

            # check if ISSN-L is good. this is here because of fatcat import
            out['known_issnl'] = (self.issn2issnl(issnl) == issnl)
            if not out['known_issnl']:
                counts['unknown-issnl'] += 1
            out['valid_issnl'] = stdnum.issn.is_valid(issnl)
            if not out['valid_issnl']:
                counts['invalid-issnl'] += 1

            fatcat_row = list(self.db.execute("SELECT * FROM fatcat_container WHERE issnl = ?;", [issnl]))
            if fatcat_row:
                frow = fatcat_row[0]
                out['fatcat_ident'] = frow['ident']
                for k in ('name', 'publisher', 'issne', 'issnp', 'wikidata_qid', 'lang', 'country', 'release_count', 'ia_count', 'ia_frac', 'kbart_count', 'kbart_frac', 'preserved_count', 'preserved_frac'):
                    if not out.get(k) and frow[k] != None:
                        out[k] = frow[k]

            cur = self.db.execute("SELECT * FROM directory WHERE issnl = ?;", [issnl])
            for irow in cur:
                if irow['slug'] in ('crossref',):
                    out['has_dois'] = True
                # TODO: other DOI registrars (japan, datacite)
                if irow['slug'] == 'wikidata':
                    out['wikidata_qid'] = irow['identifier']
                for k in ('name',):
                    if not out.get(k) and irow[k]:
                        out[k] = irow[k]
                if irow['extra']:
                    extra = json.loads(irow['extra'])
                    for k in ('country', 'lang', 'issne', 'issnp', 'publisher'):
                        if not out.get(k) and extra.get(k):
                            out[k] = extra[k]
                if irow['slug'] in ('doaj','road','szczepanski', 'gold_oa'):
                    out['is_oa'] = True
                if irow['slug'] == 'ezb':
                    ezb_extra = json.loads(irow['extra'])
                    if ezb_extra['ezb_color'] == 'green':
                        out['is_oa'] = True
                if irow['slug'] == 'sherpa_romeo':
                    extra = json.loads(irow['extra'])
                    out['sherpa_color'] = extra['color']
                    if extra['color'] == 'green':
                        out['is_oa'] = True

            # filter out "NA" ISSNs
            for k in ('issne', 'issnp'):
                if out.get(k) and (len(out[k]) != 9 or out[k][4] != '-'):
                    out.pop(k)

            cur = self.db.execute("SELECT * FROM homepage WHERE issnl = ?;", [issnl])
            for hrow in cur:
                out['any_homepage'] = True
                if hrow['terminal_status_code'] == 200 and hrow['host'] != 'web.archive.org':
                    out['any_live_homepage'] = True
                if hrow['gwb_url_success_dt'] or hrow['gwb_terminal_url_success_dt']:
                    out['any_gwb_homepage'] = True

            if out.get('wikidata_qid'):
                assert out['wikidata_qid'].startswith('Q')
                assert out['wikidata_qid'][1].isdigit()
                assert out['wikidata_qid'][-1].isdigit()

            # define publisher types
            publisher = out.get('publisher')
            pl = out.get('publisher', '').lower().strip()
            if publisher in BIG5_PUBLISHERS or 'elsevier' in pl or 'springer' in pl or 'wiley' in pl:
                out['publisher_type'] = 'big5'
            elif publisher in OA_PUBLISHERS:
                out['publisher_type'] = 'oa'
            elif publisher in COMMERCIAL_PUBLISHERS or 'wolters kluwer' in pl or 'wolters-kluwer' in pl:
                out['publisher_type'] = 'commercial'
            elif publisher in ARCHIVE_PUBLISHERS:
                out['publisher_type'] = 'archive'
            elif publisher in REPOSITORY_PUBLISHERS:
                out['publisher_type'] = 'repository'
            elif publisher in OTHER_PUBLISHERS:
                out['publisher_type'] = 'other'
            elif publisher in SOCIETY_PUBLISHERS or 'society' in pl or 'association' in pl or 'academy of ' in pl or 'institute of' in pl:
                out['publisher_type'] = 'society'
            elif publisher in UNI_PRESS_PUBLISHERS or 'university ' in pl:
                out['publisher_type'] = 'unipress'
            elif 'scielo' in pl:
                out['publisher_type'] = 'scielo'
            elif out.get('is_oa') and (not out.get('has_dois') or out.get('lang') not in (None, 'en', 'de', 'fr', 'ja') or out.get('country') not in (None, 'us', 'gb', 'nl', 'cn', 'jp', 'de')):
                # current definition of longtail
                out['publisher_type'] = 'longtail'
                out['is_longtail'] = True

            cur.execute("INSERT OR REPLACE INTO journal (issnl, issne, issnp, wikidata_qid, fatcat_ident, name, publisher, country, lang, is_oa, sherpa_color, is_longtail, is_active, publisher_type, has_dois, any_homepage, any_live_homepage, any_gwb_homepage, known_issnl, valid_issnl, release_count, ia_count, ia_frac, kbart_count, kbart_frac, preserved_count, preserved_frac) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (issnl,
                 out.get('issne'),
                 out.get('issnp'),
                 out.get('wikidata_qid'),
                 out.get('fatcat_ident'),
                 out.get('name'),
                 out.get('publisher'),
                 out.get('country'),
                 out.get('lang'),
                 out.get('is_oa', False),
                 out.get('sherpa_color'),
                 out.get('is_longtail', False),
                 out.get('is_active'),
                 out.get('publisher_type'),
                 out.get('has_dois', False),
                 out.get('any_homepage', False),
                 out.get('any_live_homepage', False),
                 out.get('any_gwb_homepage', False),
                 out.get('known_issnl'),
                 out.get('valid_issnl'),

                 out.get('release_count'),
                 out.get('ia_count'),
                 out.get('ia_frac'),
                 out.get('kbart_count'),
                 out.get('kbart_frac'),
                 out.get('preserved_count'),
                 out.get('preserved_frac'),
                ))
        cur.close()
        self.db.commit()
        print(counts)

    def everything(self, args):
        self.init_db(args)
        self.index_doaj(args)
        self.index_norwegian(args)
        self.index_crossref(args)
        self.index_sherpa_romeo(args)
        self.index_road(args)
        self.index_entrez(args)
        self.index_ezb(args)
        self.index_szczepanski(args)
        self.index_gold_oa(args)
        self.index_openapc(args)
        self.index_wikidata(args)
        self.load_fatcat(args)
        self.load_fatcat_stats(args)
        #self.preserve_kbart('lockss', LOCKSS_FILE)
        #self.preserve_kbart('clockss', CLOCKSS_FILE)
        #self.preserve_kbart('portico', PORTICO_FILE)
        #self.preserve_kbart('jstor', JSTOR_FILE)
        #self.preserve_sim(args)
        self.update_url_status(args)
        self.summarize(args)
        print("### Done with everything!")

    def export(self, args):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        counts = Counter()
        self.db.row_factory = dict_factory
        cur = self.db.cursor()
        for row in cur.execute('SELECT * FROM journal'):
            print(json.dumps(row))
            counts['total'] += 1

    def export_fatcat(self, args):
        counts = Counter()
        self.db.row_factory = sqlite3.Row
        cur = self.db.cursor()
        for row in cur.execute('SELECT * FROM journal WHERE valid_issnl = 1'):
            counts['total'] += 1

            name = row['name']
            if name:
                name = name.strip()

            if not row['name']:
                counts['empty-name'] += 1
                continue

            if len(name) <= 2:
                counts['short-name'] += 1
                continue

            publisher = row['publisher']
            if publisher:
                publisher = publisher.strip() or None

            out = dict(
                issnl=row['issnl'],
                wikidata_qid=row['wikidata_qid'],
                ident=row['fatcat_ident'],
                publisher=publisher,
                name=name,
                _known_issnl=row['known_issnl'])

            extra = dict(
                issnp=row['issnp'],
                issne=row['issne'],
                country=row['country'],
            )
            if row['lang']:
                extra['languages'] = [row['lang'],]
            if row['sherpa_color']:
                extra['sherpa_romeo'] = dict(color=row['sherpa_color'])

            urls = []
            webarchive_urls = []
            cur = self.db.execute("SELECT * FROM homepage WHERE issnl = ?;", [row['issnl']])
            for hrow in cur:
                if '://doaj.org/' in hrow['url'] or '://www.doaj.org/' in hrow['url']:
                    continue
                if '://www.ncbi.nlm.nih.gov/' in hrow['url']:
                    continue
                if 'web.archive.org/web' in hrow['url']:
                    webarchive_urls.append(hrow['url'])
                    urls.append(hrow['url'])
                    continue
                if hrow['host'] in ('www.google.com', 'books.google.com'):
                    # individual books or google searches, not journal/conference homepages
                    continue
                if '/oai/request' in hrow['url']:
                    # OAI-PMH endpoints, not homepages
                    continue
                if not row['any_live_homepage'] and hrow['gwb_url_success_dt'] and hrow['gwb_url_success_dt'] != 'error':
                    webarchive_urls.append("https://web.archive.org/web/{}/{}".format(hrow['gwb_url_success_dt'], hrow['url']))
                    continue
                if hrow['blocked']:
                    urls.append(hrow['url'])
                    continue
                if hrow['terminal_status_code'] == 200:
                    if hrow['terminal_url'] == hrow['url'].replace('http://', 'https://') or hrow['terminal_url'] == hrow['url'] + "/":
                        # check for trivial redirects; use post-redirect URL in those cases
                        urls.append(hrow['terminal_url'])
                    else:
                        urls.append(hrow['url'])
                    continue
                # didn't even crawl and no match? add anyways as a pass-through
                if not hrow['status_code']:
                    urls.append(hrow['url'])
                    continue
            extra['webarchive_urls'] = webarchive_urls
            extra['urls'] = urls

            cur = self.db.execute("SELECT * FROM directory WHERE issnl = ?;", [row['issnl']])
            for drow in cur:
                if drow['slug'] == 'ezb':
                    ezb = json.loads(drow['extra'])
                    extra['ezb'] = dict(ezb_id=drow['identifier'], color=ezb['ezb_color'])
                if drow['slug'] == 'szczepanski':
                    # XXX: pull from record
                    extra['szczepanski'] = dict(as_of=config.szczepanski.date)
                if drow['slug'] == 'doaj':
                    extra['doaj'] = json.loads(drow['extra'])

            out['extra'] = extra
            print(json.dumps(out))

    def init_db(self):
        print("### Creating Database...", file=sys.stderr)
        self.db.executescript("""
            PRAGMA main.page_size = 4096;
            PRAGMA main.cache_size = 20000;
            PRAGMA main.locking_mode = EXCLUSIVE;
            PRAGMA main.synchronous = OFF;
        """)
        with open('chocula_schema.sql', 'r') as fschema:
            self.db.executescript(fschema.read())
        print("Done!", file=sys.stderr)

