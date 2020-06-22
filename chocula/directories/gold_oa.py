from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class GoldOALoader(DirectoryLoader):
    """
    CSV Columns:

        # "ISSN","ISSN_L","ISSN_IN_DOAJ","ISSN_IN_ROAD","ISSN_IN_PMC","ISSN_IN_OAPC","ISSN_IN_WOS","ISSN_IN_SCOPUS","JOURNAL_IN_DOAJ","JOURNAL_IN_ROAD","JOURNAL_IN_PMC","JOURNAL_IN_OAPC","JOURNAL_IN_WOS","JOURNAL_IN_SCOPUS","TITLE","TITLE_SOURCE"
    """

    source_slug = "gold_oa"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.gold_oa.filepath, encoding="ISO-8859-1"))

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        if not (row.get("ISSN_L") and row.get("TITLE")):
            return None

        # TODO: also add for other non-direct indices
        # for ind in ('WOS', 'SCOPUS'):
        #    issnl, status = self.add_issn(
        #        ind.lower(),
        #        raw_issn=row['ISSN_L'],
        #        name=row['TITLE'],
        #    )

        extra = dict()
        for ind in ("DOAJ", "ROAD", "PMC", "OAPC", "WOS", "SCOPUS"):
            extra["in_" + ind.lower()] = bool(int(row["JOURNAL_IN_" + ind]))

        return DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=row["ISSN_L"],
            name=clean_str(row["TITLE"]),
            extra=extra,
        )
