
from typing import Iterable, Optional
import json

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class SzczepanskiLoader(DirectoryLoader):
    """
    CSV Columns:

    """

    source_slug = "szczepanski"

    def open_file(self) -> Iterable:
        return open(self.config.SZCZEPANSKI_FILE, 'r')

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        if not row:
            return None

        row = json.loads(row)

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issne=row.get('issne'),
            issnp=row.get('issnp'),
            raw_issn=row.get('issn'),
            name=clean_str(row['title']),
            publisher=clean_str(row.get('ed')),
        )

        info.extra['szczepanski'] = dict(as_of=self.config.SZCZEPANSKI_DATE)
        if row.get('extra'):
            info.extra['szczepanski']['notes'] = row.get('extra')
        for k in ('other_titles', 'year_spans', 'ed'):
            if row.get(k):
                info.extra['szczepanski'][k] = row[k]

        url = HomepageUrl.from_url(row.get('url'))
        if url:
            info.homepage_urls.append(url)

        return info
