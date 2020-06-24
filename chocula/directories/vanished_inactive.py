import csv
from typing import Iterable, Optional

from chocula.util import clean_str, clean_issn, parse_lang, parse_country
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class VanishedInactiveLoader(DirectoryLoader):
    """
    Journal-level metadata from the "Vanished Journals" project. This is the
    "inactive" dataset.

    CSV headers:

        - Source
        - Title
        - Identifier
        - Publisher
        - Comment
        - Language
        - ISSN
        - EISSN
        - Keyword
        - Start Year
        - End Year
        - Added on date
        - Subjects
        - Country
        - Publication fee
        - Further Information
    """

    source_slug = "vanished_inactive"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.vanished_inactive.filepath))

    def parse_record(self, record) -> Optional[DirectoryInfo]:

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=clean_issn(record["ISSN"]),
            issne=clean_issn(record["EISSN"]),
            name=clean_str(record["Title"]),
            publisher=clean_str(record["Publisher"]),
            langs=[parse_lang(record["Language"])],
            country=parse_country(record["Country"]),
        )
        return info
