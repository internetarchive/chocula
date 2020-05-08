
from typing import Iterable, Optional, Dict, Any
import csv

from chocula.util import clean_str, parse_mimetypes, parse_country, parse_lang, PLATFORM_MAP
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class DoajLoader(DirectoryLoader):
    """
    CSV Columns:

    - Journal title
    - Journal URL
    - Alternative title
    - Journal ISSN (print version)
    - Journal EISSN (online version)
    - Publisher
    - Society or institution
    - "Platform
    - host or aggregator"
    - Country of publisher
    - Journal article processing charges (APCs)
    - APC information URL
    - APC amount
    - Currency
    - Journal article submission fee
    - Submission fee URL
    - Submission fee amount
    - Submission fee currency
    - Number of articles publish in the last calendar year
    - Number of articles information URL
    - Journal waiver policy (for developing country authors etc)
    - Waiver policy information URL
    - Digital archiving policy or program(s)
    - Archiving: national library
    - Archiving: other
    - Archiving infomation URL
    - Journal full-text crawl permission
    - Permanent article identifiers
    - Journal provides download statistics
    - Download statistics information URL
    - First calendar year journal provided online Open Access content
    - Full text formats
    - Keywords
    - Full text language
    - URL for the Editorial Board page
    - Review process
    - Review process information URL
    - URL for journal's aims & scope
    - URL for journal's instructions for authors
    - Journal plagiarism screening policy
    - Plagiarism information URL
    - Average number of weeks between submission and publication
    - URL for journal's Open Access statement
    - Machine-readable CC licensing information embedded or displayed in articles
    - URL to an example page with embedded licensing information
    - Journal license
    - License attributes
    - URL for license terms
    - Does this journal allow unrestricted reuse in compliance with BOAI?
    - Deposit policy directory
    - Author holds copyright without restrictions
    - Copyright information URL
    - Author holds publishing rights without restrictions
    - Publishing rights information URL
    - DOAJ Seal
    - Tick: Accepted after March 2014
    - Added on Date
    - Subjects
    """

    source_slug = "doaj"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.doaj.filepath))

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        # TODO: Subjects, Permanent article identifiers, work_level stuff

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnp=row['Journal ISSN (print version)'],
            issne=row['Journal EISSN (online version)'],
            name=clean_str(row['Journal title']),
            publisher=clean_str(row['Publisher']),
            platform=PLATFORM_MAP.get(row['Platform, host or aggregator']),
            country=parse_country(row['Country of publisher']),
        )

        lang = parse_lang(row['Full text language'])
        if lang:
            info.langs.append(lang)

        extra: Dict[str, Any] = dict(doaj=dict())
        extra['mimetypes'] = parse_mimetypes(row['Full text formats'])
        extra['doaj']['as_of'] = self.config.doaj.date
        if row['DOAJ Seal']:
            extra['doaj']['seal'] = {"no": False, "yes": True}[row['DOAJ Seal'].lower()]

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

        url = row['Journal URL']
        if url:
            homepage = HomepageUrl.from_url(row['Journal URL'])
            if homepage:
                info.homepage_urls.append(homepage)
        return info

