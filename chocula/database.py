
import csv
import json
from collections import Counter
import sqlite3

import ftfy
import stdnum.issn

from chocula.config import *
from chocula.util import *

################### Main Class

class ChoculaDatabase():

    def __init__(self, db_file):
        self._issn_issnl_map = dict()
        self.db = sqlite3.connect(db_file, isolation_level='EXCLUSIVE')
        self.data = dict()
        self.c = None

    def read_issn_map_file(self, issn_map_path):
        print("##### Loading ISSN-L map file...")
        with open(issn_map_path, 'r') as issn_map_file:
            self._issn_issnl_map = dict()
            for line in issn_map_file:
                if line.startswith("ISSN") or len(line) == 0:
                    continue
                (issn, issnl) = line.split()[0:2]
                self._issn_issnl_map[issn] = issnl
                # double mapping makes lookups easy
                self._issn_issnl_map[issnl] = issnl
        print("Got {} ISSN-L mappings.".format(len(self._issn_issnl_map)))

    def issn2issnl(self, issn):
        if issn is None:
            return None
        return self._issn_issnl_map.get(issn)

    def add_issn(self, index_slug, raw_issn=None, issne=None, issnp=None, identifier=None, name=None, publisher=None, extra=None):

        # do ISSN => ISSN-L mappings for any raw ISSNs
        issnl = None
        if not (raw_issn or issne or issnp):
            return None, 'no-issn'
        for lookup in (issnp, issne, raw_issn):
            if not lookup:
                continue
            lookup = lookup.strip().upper()
            #if not (len(lookup) == 9 and lookup[4] == '-'):
            #    print(lookup)
            #    print(len(lookup))
            #    print(lookup[4])
            #    return None, 'invalid-issn'
            #assert len(lookup) == 9 and lookup[4] == '-'
            issnl = self.issn2issnl(lookup)
            if issnl:
                break
        if not issnl:
            return None, 'unknown-issnl'
            #print((raw_issn, issne, issnp))
            # UGH.
            #issnl = issne or issnp or raw_issn
            #if not issnl:
            #issnl = issnl.strip().upper()
            #assert len(issnl) == 9 and issnl[4] == '-'
            #status = 'found-munge'
        else:
            status = 'found'

        if extra == None:
            extra = dict()

        if issne:
            extra['issne'] = issne
        if issnp:
            extra['issnp'] = issnp

        if publisher:
            publisher = unquote(ftfy.fix_text(publisher))
        if publisher:
            extra['publisher'] = publisher

        if extra:
            extra = json.dumps(extra)
        else:
            extra = None

        try:
            self.c.execute("INSERT INTO directory VALUES (?,?,?,?,?)",
                (issnl, index_slug, identifier, name, extra))
            status = 'inserted'
        except sqlite3.IntegrityError as ie:
            if str(ie).startswith("UNIQUE"):
                return None, "duplicate-issnl"
            raise ie

        return issnl, status

    def add_url(self, issnl, url):
        if not (issnl and url):
            return
        meta = parse_url(url)
        if not meta:
            return

        self.c.execute("INSERT OR REPLACE INTO homepage (issnl, surt, url, host, domain, suffix) VALUES (?,?,?,?,?,?)",
            (issnl,
             meta['url_surt'],
             meta['url'],
             meta['host'],
             meta['registered_domain'],
             meta['suffix']
            ))

    def index_entrez(self, args):
        path = args.input_file or ENTREZ_FILE
        print("##### Loading Entrez...")
        # JrId,JournalTitle,MedAbbr,"ISSN (Print)","ISSN (Online)",IsoAbbr,NlmId
        reader = csv.DictReader(open(path))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            if not (row.get('ISSN (Online)') or row.get('ISSN (Print)')):
                counts['skipped'] += 1
                continue
            extra = dict()
            if row['IsoAbbr']:
               extra['abbrev'] = row['IsoAbbr'].strip()
            issnl, status = self.add_issn(
                'entrez',
                issne=row.get('ISSN (Online)'),
                issnp=row.get('ISSN (Print)'),
                name=row['JournalTitle'],
                extra=extra,
            )
            counts[status] += 1
        self.c.close()
        self.db.commit()
        print(counts)

    def index_road(self, args):
        path = args.input_file or ROAD_FILE
        print("##### Loading ROAD...")
        reader = csv.DictReader(open(path), delimiter='\t',
            fieldnames=("ISSN", "ISSN-L", "Short Title", "Title", "Publisher", "URL1", "URL2", "Region", "Lang1", "Lang2")
        )
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            extra = dict()
            if row['Lang1']:
                extra['langs'] = [row['Lang1']]
            if row['Lang2']:
                extra['langs'].append(row['Lang2'])
            # TODO: region mapping: "Europe and North America"
            # TODO: lang mapping: already alpha-3
            issnl, status = self.add_issn(
                'road',
                raw_issn=row['ISSN-L'],
                name=row['Short Title'],
                publisher=row['Publisher'],
            )
            counts[status] += 1
            if not issnl:
                continue
            if row['URL1']:
                self.add_url(issnl, row['URL1'])
            if row['URL2']:
                self.add_url(issnl, row['URL2'])
        self.c.close()
        self.db.commit()
        print(counts)

    def index_doaj(self, args):
        path = args.input_file or DOAJ_FILE
        print("##### Loading DOAJ...")
        #Journal title,Journal URL,Alternative title,Journal ISSN (print version),Journal EISSN (online version),Publisher,Society or institution,"Platform, host or aggregator",Country of publisher,Journal article processing charges (APCs),APC information URL,APC amount,Currency,Journal article submission fee,Submission fee URL,Submission fee amount,Submission fee currency,Number of articles publish in the last calendar year,Number of articles information URL,Journal waiver policy (for developing country authors etc),Waiver policy information URL,Digital archiving policy or program(s),Archiving: national library,Archiving: other,Archiving infomation URL,Journal full-text crawl permission,Permanent article identifiers,Journal provides download statistics,Download statistics information URL,First calendar year journal provided online Open Access content,Full text formats,Keywords,Full text language,URL for the Editorial Board page,Review process,Review process information URL,URL for journal's aims & scope,URL for journal's instructions for authors,Journal plagiarism screening policy,Plagiarism information URL,Average number of weeks between submission and publication,URL for journal's Open Access statement,Machine-readable CC licensing information embedded or displayed in articles,URL to an example page with embedded licensing information,Journal license,License attributes,URL for license terms,Does this journal allow unrestricted reuse in compliance with BOAI?,Deposit policy directory,Author holds copyright without restrictions,Copyright information URL,Author holds publishing rights without restrictions,Publishing rights information URL,DOAJ Seal,Tick: Accepted after March 2014,Added on Date,Subjects
        # TODO: Subjects, Permanent article identifiers, work_level stuff
        reader = csv.DictReader(open(path))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:

            extra = dict(as_of=DOAJ_DATE)
            extra['mimetypes'] = parse_mimetypes(row['Full text formats'])
            platform = PLATFORM_MAP.get(row['Platform, host or aggregator'])
            if platform:
                extra['platform'] = platform
            if row['DOAJ Seal']:
                extra['seal'] = {"no": False, "yes": True}[row['DOAJ Seal'].lower()]
            if row['Country of publisher']:
                extra['country'] = parse_country(row['Country of publisher'])
            row['lang'] = parse_lang(row['Full text language'])

            if row['Digital archiving policy or program(s)']:
                extra['archive'] = [a.strip() for a in row['Digital archiving policy or program(s)'].split(',') if a.strip()]
            elif row['Archiving: national library']:
                extra['archive'] = ['national-library']

            crawl_permission = row['Journal full-text crawl permission']
            if crawl_permission:
                extra['crawl-permission'] = dict(Yes=True, No=False)[crawl_permission]
            default_license = row['Journal license']
            if default_license and default_license.startswith('CC'):
                extra['default_license'] = default_license.replace('CC ', 'CC-').strip()

            issnl, status = self.add_issn(
                'doaj',
                issnp=row['Journal ISSN (print version)'],
                issne=row['Journal EISSN (online version)'],
                name=row['Journal title'],
                publisher=row['Publisher'],
                extra=extra,
            )
            if row['Journal URL']:
                self.add_url(issnl, row['Journal URL'])
            counts[status] += 1

        self.c.close()
        self.db.commit()
        print(counts)

    def index_sherpa_romeo(self, args):
        journal_path = args.input_file or SHERPA_ROMEO_JOURNAL_FILE
        policy_path = SHERPA_ROMEO_POLICY_FILE
        # first load policies
        print("##### Loading SHERPA/ROMEO policies...")
        #RoMEO Record ID,Publisher,Policy Heading,Country,RoMEO colour,Published Permission,Published Restrictions,Published Max embargo,Accepted Prmission,Accepted Restrictions,Accepted Max embargo,Submitted Permission,Submitted Restrictions,Submitted Max embargo,Open Access Publishing,Record Status,Updated
        policies = dict()
        fixed_policy_file = ftfy.fix_file(open(policy_path, 'rb'))
        policy_reader = csv.DictReader(fixed_policy_file)
        for row in policy_reader:
            policies[row['RoMEO Record ID']] = row
        print("##### Loading SHERPA/ROMEO journal metadata...")
        #Journal Title,ISSN,ESSN,URL,RoMEO Record ID,Updated
        # super mangled :(
        raw_file = open(journal_path, 'rb').read().decode(errors='replace')
        fixed_file = ftfy.fix_text(raw_file)
        reader = csv.DictReader(fixed_file.split('\n'))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            #row['Journal Title'] = row.pop('\ufeffJournal Title')
            row.update(policies[row['RoMEO Record ID']])
            extra = dict()
            if row['RoMEO colour']:
                extra['color'] = row['RoMEO colour']
            # row['Open Access Publishing']
            if row['Country']:
                extra['country'] = parse_country(row['Country'])
            issnl, status = self.add_issn(
                'sherpa_romeo',
                issnp=row['ISSN'],
                issne=row['ESSN'],
                name=row['Journal Title'],
                publisher=row['Publisher'],
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
        self.c.close()
        self.db.commit()
        print(counts)

    def index_norwegian(self, args):
        path = args.input_file or NORWEGIAN_FILE
        print("##### Loading Norwegian Registry...")
        #pandas.read_csv(NORWEGIAN_FILE, sep=';', encoding="ISO-8859-1")
        # Old: NSD tidsskrift_id;Original title;International title;Present Level (2018);Print ISSN;Online ISSN;Open Access;NPI Scientific Field;NPI Academic Discipline;URL;Publishing Company;Publisher;Country of publication;Language;Level 2019;Level 2018;Level 2017;Level 2016;Level 2015;Level 2014;Level 2013;Level 2012;Level 2011;Level 2010;Level 2009;Level 2008;Level 2007;Level 2006;Level 2005;Level 2004;itar_id
        # New: NSD tidsskrift_id;Original title;International title;Print ISSN;Online ISSN;Open Access;NPI Academic Discipline;NPI Scientific Field;Level 2020;Level 2019;Level 2018;Level 2017;Level 2016;Level 2015;Level 2014;Level 2013;Level 2012;Level 2011;Level 2010;Level 2009;Level 2008;Level 2007;Level 2006;Level 2005;Level 2004;itar_id;NSD forlag_id;Publishing Company;Publisher;Country of publication;Language;Conference Proceedings;Established;Ceased;URL
        reader = csv.DictReader(open(path, encoding="ISO-8859-1"), delimiter=";")
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            issnp = row['Print ISSN']
            issne = row['Online ISSN']
            if issne and len(issne.strip()) != 9:
                issne = None
            if issnp and len(issnp.strip()) != 9:
                issnp = None
            if not (issnp or issne):
                counts['no-issn'] += 1
                continue
            extra = dict(as_of=NORWEGIAN_DATE)
            if row['Level 2019']:
                extra['level'] = int(row['Level 2019'])
            if row['Original title'] != row['International title']:
                extra['original_name'] = row['Original title']
            if row['Country of publication']:
                extra['country'] = parse_country(row['Country of publication'])
            if row['Language']:
                extra['lang'] = parse_lang(row['Language'])
            issnl, status = self.add_issn(
                'norwegian',
                issnp=issnp,
                issne=issne,
                identifier=row['NSD tidsskrift_id'],
                name=row['International title'],
                publisher=row['Publisher'],
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            if row['URL']:
                self.add_url(issnl, row['URL'])
        self.c.close()
        self.db.commit()
        print(counts)

    def index_szczepanski(self, args):
        path = args.input_file or SZCZEPANSKI_FILE
        print("##### Loading Szczepanski...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        self.c = self.db.cursor()
        for row in json_file:
            if not row:
                continue
            row = json.loads(row)
            if not (row.get('issne') or row.get('issnp') or row.get('issn')):
                #print(row)
                counts['no-issn'] += 1
                continue
            extra = dict(as_of=SZCZEPANSKI_DATE)
            if row.get('extra'):
                extra['notes'] = row.get('extra')
            for k in ('other_titles', 'year_spans', 'ed'):
                if row.get(k):
                    extra[k] = row[k]
            issnl, status = self.add_issn(
                'szczepanski',
                issne=row.get('issne'),
                issnp=row.get('issnp'),
                raw_issn=row.get('issn'),
                name=row['title'],
                publisher=row.get('ed'),
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            for url in row.get('urls', []):
                self.add_url(issnl, url['url'])
        self.c.close()
        self.db.commit()
        print(counts)

    def index_ezb(self, args):
        path = args.input_file or EZB_FILE
        print("##### Loading EZB...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        self.c = self.db.cursor()
        for row in json_file:
            if not row:
                continue
            row = json.loads(row)
            if not (row.get('issne') or row.get('issnp')):
                #print(row)
                counts['no-issn'] += 1
                continue
            extra = dict()
            for k in ('ezb_color', 'subjects', 'keywords', 'zdb_id',
                      'first_volume', 'first_issue', 'first_year',
                      'appearance', 'costs'):
                if row.get(k):
                    extra[k] = row[k]
            issnl, status = self.add_issn(
                'ezb',
                issne=row.get('issne'),
                issnp=row.get('issnp'),
                identifier=row['ezb_id'],
                name=row['title'],
                publisher=row.get('publisher'),
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            if row.get('url'):
                self.add_url(issnl, row['url'])
        self.c.close()
        self.db.commit()
        print(counts)

    def index_gold_oa(self, args):
        path = args.input_file or GOLD_OA_FILE
        print("##### Loading GOLD OA...")
        # "ISSN","ISSN_L","ISSN_IN_DOAJ","ISSN_IN_ROAD","ISSN_IN_PMC","ISSN_IN_OAPC","ISSN_IN_WOS","ISSN_IN_SCOPUS","JOURNAL_IN_DOAJ","JOURNAL_IN_ROAD","JOURNAL_IN_PMC","JOURNAL_IN_OAPC","JOURNAL_IN_WOS","JOURNAL_IN_SCOPUS","TITLE","TITLE_SOURCE"
        reader = csv.DictReader(open(path, encoding="ISO-8859-1"))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            if not (row.get('ISSN_L') and row.get('TITLE')):
                counts['skipped'] += 1
                continue
            extra = dict()
            for ind in ('DOAJ', 'ROAD', 'PMC', 'OAPC', 'WOS', 'SCOPUS'):
                extra['in_' + ind.lower()] = bool(int(row['JOURNAL_IN_' + ind]))
            issnl, status = self.add_issn(
                'gold_oa',
                raw_issn=row['ISSN_L'],
                name=row['TITLE'],
                extra=extra,
            )
            counts[status] += 1
            # also add for other non-direct indices
            for ind in ('WOS', 'SCOPUS'):
                issnl, status = self.add_issn(
                    ind.lower(),
                    raw_issn=row['ISSN_L'],
                    name=row['TITLE'],
                )
        self.c.close()
        self.db.commit()
        print(counts)

    def index_wikidata(self, args):
        path = args.input_file or WIKIDATA_SPARQL_FILE
        print("##### Loading Wikidata...")
        reader = csv.DictReader(open(path), delimiter='\t')
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            if not (row.get('issn') and row.get('title')):
                counts['skipped'] += 1
                continue
            publisher = row['publisher_name']
            if (publisher.startswith('Q') and publisher[1].isdigit()) or publisher.startswith('t1') or not publisher:
                publisher = None
            wikidata_qid = row['item'].strip().split('/')[-1]
            extra = dict()
            extra['start_year'] = row.get('start_year')
            issnl, status = self.add_issn(
                'wikidata',
                raw_issn=row['issn'],
                name=row['title'],
                identifier=wikidata_qid,
                publisher=publisher,
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            if row.get('websiteurl'):
                self.add_url(issnl, row['websiteurl'])
        self.c.close()
        self.db.commit()
        print(counts)

    def index_openapc(self, args):
        path = args.input_file or OPENAPC_FILE
        print("##### Loading OpenAPC...")
        # "institution","period","euro","doi","is_hybrid","publisher","journal_full_title","issn","issn_print","issn_electronic","issn_l","license_ref","indexed_in_crossref","pmid","pmcid","ut","url","doaj"
        reader = csv.DictReader(open(path))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            if not row.get('issn'):
                counts['skipped'] += 1
                continue
            extra = dict(is_hybrid=bool(row['is_hybrid']))
            issnl, status = self.add_issn(
                'openapc',
                issne=row['issn_electronic'],
                issnp=row['issn_print'],
                raw_issn=row['issn_l'] or row['issn'],
                name=row['journal_full_title'],
                publisher=row['publisher'],
                extra=extra,
            )
            counts[status] += 1
            if not issnl:
                continue
            if row.get('url'):
                self.add_url(issnl, row['url'])
        self.c.close()
        self.db.commit()
        print(counts)

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

    def index_crossref(self, args):
        path = args.input_file or CROSSREF_FILE
        print("##### Loading Crossref...")
        #"JournalTitle","JournalID","Publisher","pissn","eissn","additionalIssns","doi","(year1)[volume1]issue1,issue2,issue3(year2)[volume2]issue4,issues5"
        reader = csv.DictReader(open(path))
        counts = Counter()
        self.c = self.db.cursor()
        for row in reader:
            if row['pissn'] and len(row['pissn']) == 8:
                row['pissn'] = row['pissn'][:4] + '-' + row['pissn'][4:]
            if row['eissn'] and len(row['eissn']) == 8:
                row['eissn'] = row['eissn'][:4] + '-' + row['eissn'][4:]
            if row['additionalIssns'] and len(row['additionalIssns']) == 8:
                row['additionalIssns'] = row['additionalIssns'][:4] + '-' + row['additionalIssns'][4:]
            if not (row['pissn'] or row['eissn'] or row['additionalIssns']):
                #print(row)
                counts['no-issn'] += 1
                continue
            extra = dict()
            issnl, status = self.add_issn(
                'crossref',
                issnp=row['pissn'],
                issne=row['eissn'],
                raw_issn=row['additionalIssns'],
                identifier=row.get('doi'),
                name=row['JournalTitle'],
                publisher=row['Publisher'],
                extra=extra,
            )
            counts[status] += 1
        self.c.close()
        self.db.commit()
        print(counts)

    def index_sim(self, args):
        path = args.input_file or SIM_FILE
        print("##### Loading SIM Metadata...")
        #NA Pub Cat ID,Title,Publisher,ISSN,Impact Rank,Total Cities,Journal Impact Factor,Eigenfact or Score,First Volume,Last Volume,NA Gaps,"Scholarly / Peer-\n Reviewed","Peer-\n Reviewed",Pub Type,Pub Language,Subjects
        reader = csv.DictReader(open(path))
        counts = Counter()
        self.c = self.db.cursor()
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
        self.c.close()
        self.db.commit()
        print(counts)

    def update_url_status(self, args):
        path = args.input_file or IA_CRAWL_FILE
        print("##### Loading IA Homepage Crawl Results...")
        counts = Counter()
        self.c = self.db.cursor()
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
            self.c.execute("UPDATE homepage SET status_code=?, crawl_error=?, terminal_url=?, terminal_status_code=?, platform_software=?, issnl_in_body=?, blocked=?, gwb_url_success_dt=?, gwb_terminal_url_success_dt=? WHERE url=?",
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
        self.c.close()
        self.db.commit()
        print(counts)

    def load_fatcat(self, args):
        path = args.input_file or FATCAT_CONTAINER_FILE
        print("##### Loading Fatcat Container Entities...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        self.c = self.db.cursor()
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
                self.c.execute("INSERT OR REPLACE INTO fatcat_container (issnl, ident, revision, issne, issnp, wikidata_qid, name, container_type, publisher, country, lang) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
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
        self.c.close()
        self.db.commit()
        print(counts)

    def load_fatcat_stats(self, args):
        path = args.input_file or FATCAT_STATS_FILE
        print("##### Loading Fatcat Container Stats...")
        # JSON
        json_file = open(path, 'r')
        counts = Counter()
        self.c = self.db.cursor()
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
            self.c.execute("UPDATE fatcat_container SET release_count = ?, ia_count = ?, ia_frac = ?, preserved_count = ?, preserved_frac = ? WHERE issnl = ?",
                (total, row['in_web'], ia_frac, row['is_preserved'], preserved_frac, row['issnl']))
            counts['updated'] += 1
        self.c.close()
        self.db.commit()
        print(counts)

    def export_urls(self, args):
        self.c = self.db.cursor()
        self.db.row_factory = sqlite3.Row
        cur = self.db.execute("SELECT issnl, url FROM homepage;")
        for hrow in cur:
            assert(hrow['url'])
            assert(len(hrow['url'].split()) == 1)
            print('\t'.join((hrow['issnl'], hrow['url'])))

    def summarize(self, args):
        print("##### Summarizing Everything...")
        counts = Counter()
        self.c = self.db.cursor()
        self.db.row_factory = sqlite3.Row
        index_issnls = list(self.c.execute('SELECT DISTINCT issnl FROM directory'))
        fatcat_issnls = list(self.c.execute('SELECT DISTINCT issnl FROM fatcat_container WHERE issnl IS NOT null'))
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

            self.c.execute("INSERT OR REPLACE INTO journal (issnl, issne, issnp, wikidata_qid, fatcat_ident, name, publisher, country, lang, is_oa, sherpa_color, is_longtail, is_active, publisher_type, has_dois, any_homepage, any_live_homepage, any_gwb_homepage, known_issnl, valid_issnl, release_count, ia_count, ia_frac, kbart_count, kbart_frac, preserved_count, preserved_frac) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
        self.c.close()
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
        self.c = self.db.cursor()
        for row in self.c.execute('SELECT * FROM journal'):
            print(json.dumps(row))
            counts['total'] += 1

    def export_fatcat(self, args):
        counts = Counter()
        self.db.row_factory = sqlite3.Row
        self.c = self.db.cursor()
        for row in self.c.execute('SELECT * FROM journal WHERE valid_issnl = 1'):
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
                    extra['szczepanski'] = dict(as_of=SZCZEPANSKI_DATE)
                if drow['slug'] == 'doaj':
                    extra['doaj'] = json.loads(drow['extra'])

            out['extra'] = extra
            print(json.dumps(out))

    def init_db(self, args):
        print("### Creating Database...")
        self.db.executescript("""
            PRAGMA main.page_size = 4096;
            PRAGMA main.cache_size = 20000;
            PRAGMA main.locking_mode = EXCLUSIVE;
            PRAGMA main.synchronous = OFF;
        """)
        with open('chocula_schema.sql', 'r') as fschema:
            self.db.executescript(fschema.read())
        print("Done!")

