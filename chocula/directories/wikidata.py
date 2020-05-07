
from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class WikidataLoader(DirectoryLoader):
    """
    CSV Columns:

    """

    source_slug = "wikidata"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.WIKIDATA_SPARQL_FILE), delimiter='\t')

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        if not (row.get('issn') and row.get('title')):
            return None
        wikidata_qid = row['item'].strip().split('/')[-1]
        publisher = row['publisher_name']
        if (publisher.startswith('Q') and publisher[1].isdigit()) or publisher.startswith('t1') or not publisher:
            publisher = None
        info =DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=row['issn'],
            custom_id=wikidata_qid,
            name=clean_str(row['title']),
            publisher=clean_str(publisher),
        )
        if row.get('start_year'):
            info.extra['start_year'] = row['start_year']

        url = HomepageUrl.from_url(row.get('websiteurl'))
        if url:
            info.homepage_urls.append(url)

        return info
