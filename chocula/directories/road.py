
from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class RoadLoader(DirectoryLoader):
    """
    CSV Columns:

    - ISSN
    - ISSN-L
    - Short Title
    - Title
    - Publisher
    - URL1
    - URL2
    - Region
    - Lang1
    - Lang2
    """

    source_slug = "road"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.ROAD_FILE), delimiter='\t',
            fieldnames=("ISSN", "ISSN-L", "Short Title", "Title", "Publisher", "URL1", "URL2", "Region", "Lang1", "Lang2")
        )

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=row['ISSN-L'],
            name=clean_str(row['Short Title']),
            publisher=clean_str(row['Publisher']),
            langs=[l for l in (row['Lang1'], row['Lang2']) if l],
        )

        # TODO: region mapping: "Europe and North America"
        # TODO: lang mapping: already alpha-3

        # homepages
        for url in [u for u in (row['URL1'], row['URL2']) if u]:
            homepage = HomepageUrl.from_url(url)
            if homepage:
                info.homepage_urls.append(homepage)

        return info

