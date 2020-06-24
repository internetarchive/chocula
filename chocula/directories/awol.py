from typing import Iterable, Optional
import json

from chocula.util import clean_str, clean_issn
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class AwolLoader(DirectoryLoader):
    """
    AWOL: Ancient World Online index

    JSON keys:

        "authors",
        "contributors",
        "description",
        "domain",
        "editors",
        "end_date",
        "extent",
        "form",
        "frequency",
        "identifiers",
        "is_part_of",
        "issuance",
        "issue",
        "issued_dates",
        "keywords",
        "languages",
        "places",
        "provenance",
        "publishers",
        "related_resources",
        "resource_key",
        "responsibility",
        "start_date",
        "subordinate_resources",
        "title",
        "title_alternates",
        "title_extended",
        "type",
        "url",
        "url_alternates",
        "volume",
        "year",
        "zenon_id",
        "zotero_id"
    """

    source_slug = "awol"

    def open_file(self) -> Iterable:
        return open(self.config.awol.filepath)

    def parse_record(self, line) -> Optional[DirectoryInfo]:
        record = json.loads(line)

        issn_info = record.get("identifiers", {}).get("issn", {})
        # sometimes is a list
        for k in "generic", "electronic", "print":
            if type(issn_info.get(k)) == list:
                issn_info[k] = issn_info[k][0]
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=clean_issn(issn_info.get("generic", "")),
            issne=clean_issn(issn_info.get("electronic", "")),
            issnp=clean_issn(issn_info.get("print", "")),
            name=clean_str(record.get("title")),
            langs=list(filter(lambda s: len(s) == 2, record["languages"])),
        )
        if record["url"]:
            homepage = HomepageUrl.from_url(record["url"])
            if homepage:
                info.homepage_urls.append(homepage)
        return info
