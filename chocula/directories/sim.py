from typing import Iterable, Optional, Dict, Any
import csv

from chocula.util import (
    clean_str,
    parse_lang,
    gaps_to_spans,
)
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


def truthy(raw: Optional[str]) -> Optional[bool]:
    if not raw:
        return None
    if raw.lower() == 'y':
        return True
    if raw.lower() == 'n':
        return False
    return None


class SimLoader(DirectoryLoader):

    source_slug = "sim"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.sim.filepath))

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        """
        NA Pub Cat ID
        Title
        Publisher
        ISSN
        Impact Rank
        Total Cities
        Journal Impact Factor
        Eigenfact or Score
        First Volume
        Last Volume
        NA Gaps
        "Scholarly / Peer-\n Reviewed"
        "Peer-\n Reviewed"
        Pub Type
        Pub Language
        Subjects
        """
        # TODO: 'Pub Type'

        extra: Dict[str, Any] = {}
        first_year = row["First Volume"]
        if first_year:
            first_year = int(first_year)
            extra["first_year"] = int(row["First Volume"])
        else:
            first_year = None
        last_year = row["Last Volume"]
        if last_year:
            last_year = int(last_year)
            extra["last_year"] = last_year
        else:
            last_year = None
        gaps = [int(g) for g in row["NA Gaps"].split(";") if g.strip()]
        if gaps:
            extra["gaps"] = gaps
        if first_year and last_year:
            extra["year_spans"] = gaps_to_spans(first_year, last_year, gaps)
        extra["scholarly_peer_reviewed"] = truthy(clean_str(row["Scholarly / Peer-\nReviewed"]))
        extra["peer_reviewed"] = truthy(clean_str(row["Peer-\nReviewed"]))
        extra["pub_type"] = clean_str(row["Pub Type"])

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            name=clean_str(row["Title"]),
            publisher=clean_str(row["Publisher"]),
            raw_issn=row["ISSN"][:9],
            custom_id=row.get("NA Pub Cat ID").strip() or None,
            langs=[lang for lang in [parse_lang(row["Pub Language"])] if lang],
            extra=extra,
        )
        return info
