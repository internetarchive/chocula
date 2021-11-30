from typing import Iterable, Optional
import csv

from chocula.util import clean_str, clean_issn
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class MagLoader(DirectoryLoader):
    """
    TSV Columns (from schema docs):

        1    JournalId    long    PRIMARY KEY
        2    Rank    uint    See FAQ
        3    NormalizedName    string
        4    DisplayName    string
        5    Issn    string
        6    Publisher    string
        7    Webpage    string
        8    PaperCount    long
        9    PaperFamilyCount    long    See FAQ
        10   CitationCount    long
        11   CreatedDate    DateTime

    """

    source_slug = "mag"

    def open_file(self) -> Iterable:
        return csv.DictReader(
            open(self.config.mag.filepath, "r"),
            delimiter="\t",
            fieldnames=[
                "JournalId",
                "Rank",
                "NormalizedName",
                "DisplayName",
                "Issn",
                "Publisher",
                "Webpage",
                "PaperCount",
                "PaperFamilyCount",
                "CitationCount",
                "CreatedDate",
            ],
        )

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=clean_issn(record["Issn"]),
            custom_id=record["JournalId"],
            name=clean_str(record["DisplayName"]),
            publisher=clean_str(record["Publisher"]),
        )
        homepage = HomepageUrl.from_url(record["Webpage"] or "")
        if homepage:
            info.homepage_urls.append(homepage)

        return info
