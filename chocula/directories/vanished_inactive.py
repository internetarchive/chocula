import csv
from typing import Iterable, Optional

from chocula.util import clean_str, clean_issn
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class VanishedInactiveLoader(DirectoryLoader):
    """
    Journal-level metadata from the "Vanished Journals" project. This is the
    "inactive" dataset.

    CSV headers:

        - Title
        - URL
        - ISSN
        - EISSN
    """

    source_slug = "vanished_inactive"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.vanished_inactive.filepath), delimiter=";")

    def parse_record(self, record) -> Optional[DirectoryInfo]:

        # HACK
        record["Title"] = record["\ufeffTitle"]
        if not record["Title"]:
            return None

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=clean_issn(record["ISSN"]),
            issne=clean_issn(record["EISSN"]),
            name=clean_str(record["Title"]),
        )

        homepage = HomepageUrl.from_url(record["URL"])
        if homepage:
            info.homepage_urls.append(homepage)
        return info
