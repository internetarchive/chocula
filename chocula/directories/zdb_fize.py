import json
from typing import Iterable, Optional

from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class ZdbFizeLoader(DirectoryLoader):
    """
    URL metadata scraped from ZDB "FIZE" interface. Consists of just ISSN / URL
    pair.

    Only interested in the homepage.
    """

    source_slug = "zdb_fize"

    def open_file(self) -> Iterable:
        return open(self.config.zdb_fize.filepath, "r")

    def parse_record(self, record) -> Optional[DirectoryInfo]:

        if not record.strip():
            return None
        record = json.loads(record)

        info = DirectoryInfo(directory_slug=self.source_slug, issnl=record["issn"])

        homepage = HomepageUrl.from_url(record["homepage"])
        if homepage:
            info.homepage_urls.append(homepage)
        else:
            return None
        return info
