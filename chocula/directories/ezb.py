
from typing import Iterable, Optional
import json

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class EzbLoader(DirectoryLoader):
    """
    CSV Columns:

    """

    source_slug = "ezb"

    def open_file(self) -> Iterable:
        return open(self.config.ezb.filepath, 'r')

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        if not row:
            return None
        row = json.loads(row)

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issne=row.get('issne'),
            issnp=row.get('issnp'),
            custom_id=row['ezb_id'],
            name=clean_str(row['title']),
            publisher=clean_str(row.get('publisher')),
        )

        info.extra = dict()
        for k in ('ezb_color', 'subjects', 'keywords', 'zdb_id',
                    'first_volume', 'first_issue', 'first_year',
                    'appearance', 'costs'):
            if row.get(k):
                info.extra[k] = row[k]

        url = HomepageUrl.from_url(row.get('url'))
        if url:
            info.homepage_urls.append(url)

        return info
