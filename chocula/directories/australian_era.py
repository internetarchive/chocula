from typing import Iterable, Optional
import csv

from chocula.util import clean_str
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class AustralianEraLoader(DirectoryLoader):
    """
    Using this primarily as

    CSV Columns (2018 file):

        ERA Journal Id
        Title
        Foreign Title
        FoR 1
        FoR 1 Name
        FoR 2
        FoR 2 Name
        FoR 3
        FoR 3 Name
        ISSN 1
        ISSN 2
        ISSN 3
        ISSN 4
        ISSN 5
        ISSN 6
        ISSN 7
    """

    source_slug = "australian_era"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.australian_era.filepath))

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=row["ISSN 1"],
            custom_id=clean_str(row["ERA Journal Id"]),
            name=clean_str(row.get("Title")),
            original_name=clean_str(row.get("Foreign Title")),
            extra=dict(
                australian_era=dict(
                    era_id=clean_str(row["ERA Journal Id"]),
                    field=clean_str(row["FoR 1 Name"]),
                    field_code=clean_str(row["FoR 1"]),
                )
            ),
        )

        return info
