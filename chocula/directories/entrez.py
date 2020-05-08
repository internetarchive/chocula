
from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class EntrezLoader(DirectoryLoader):
    """
    CSV Columns:

    - JrId
    - JournalTitle
    - MedAbbr
    - "ISSN (Print)"
    - "ISSN (Online)"
    - IsoAbbr
    - NlmId
    """

    source_slug = "entrez"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.entrez_simple.filepath))

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        if not (record.get('ISSN (Online)') or record.get('ISSN (Print)')):
            return None
        return DirectoryInfo(
            directory_slug=self.source_slug,
            issne=record.get('ISSN (Online)'),
            issnp=record.get('ISSN (Print)'),
            custom_id=record.get('NlmId').strip() or None,
            name=clean_str(record.get('JournalTitle')),
            abbrev=clean_str(record['IsoAbbr']),
        )

