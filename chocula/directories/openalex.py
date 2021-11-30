from typing import Iterable, Optional
import csv

from chocula.util import clean_str, clean_issn
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class OpenAlexLoader(DirectoryLoader):
    """
    TSV Columns (from schema docs):

        1   JournalId    long    PRIMARY KEY
        2   Rank    uint    (DEPRECATED)
        3   NormalizedName    string
        4   DisplayName    string
        5   Issn    string (ISSN-L)
        6   Issns    JSON list
        7   IsOa    bool
        8   IsInDoaj    bool
        9   Publisher    string
        10  Webpage    string
        11  PaperCount    long
        12  PaperFamilyCount    long    (DEPRECATED)
        13  CitationCount    long
        14  CreatedDate    DateTime
        15  UpdatedDate    DateTime

    """

    source_slug = "openalex"

    def open_file(self) -> Iterable:
        return csv.DictReader(
            open(self.config.openalex.filepath, "r"),
            delimiter="\t",
            fieldnames=[
                "JournalId",
                "Rank",
                "NormalizedName",
                "DisplayName",
                "Issn",
                "Issns",
                "IsOa",
                "IsInDoaj",
                "Publisher",
                "Webpage",
                "PaperCount",
                "PaperFamilyCount",
                "CitationCount",
                "CreatedDate",
                "UpdatedDate",
            ],
        )

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnl=clean_issn(record["Issn"]),
            custom_id=record["JournalId"],
            name=clean_str(record["DisplayName"]),
            publisher=clean_str(record["Publisher"]),
        )
        homepage = HomepageUrl.from_url(record["Webpage"] or "")
        if homepage:
            info.homepage_urls.append(homepage)

        return info
