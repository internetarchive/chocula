
from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class OpenAPCLoader(DirectoryLoader):
    """
    CSV Columns:

        # "institution","period","euro","doi","is_hybrid","publisher","journal_full_title","issn","issn_print","issn_electronic","issn_l","license_ref","indexed_in_crossref","pmid","pmcid","ut","url","doaj"
    """

    source_slug = "openapc"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.openapc.filepath))

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        if not row.get('issn'):
            return None

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issne=row['issn_electronic'],
            issnp=row['issn_print'],
            raw_issn=row['issn_l'] or row['issn'],
            name=clean_str(row['journal_full_title']),
            publisher=clean_str(row['publisher']),
        )

        info.extra['is_hybrid'] = bool(row['is_hybrid'])

        homepage = HomepageUrl.from_url(row['url'])
        if homepage:
            info.homepage_urls.append(homepage)

        return info


