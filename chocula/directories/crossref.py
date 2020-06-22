from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class CrossrefLoader(DirectoryLoader):
    """
    CSV Columns:

        #"JournalTitle","JournalID","Publisher","pissn","eissn","additionalIssns","doi","(year1)[volume1]issue1,issue2,issue3(year2)[volume2]issue4,issues5"

    """

    source_slug = "crossref"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.crossref.filepath))

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issne=record["eissn"],
            issnp=record["pissn"],
            custom_id=record.get("doi").strip() or None,
            name=clean_str(record.get("JournalTitle")),
            publisher=clean_str(record.get("Publisher")),
        )

        if record["additionalIssns"]:
            info.raw_issn = record["additionalIssns"][0]

        return info
