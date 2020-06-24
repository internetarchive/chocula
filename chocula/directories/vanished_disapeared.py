import csv
from typing import Iterable, Optional

from chocula.util import clean_str, clean_issn, parse_lang, parse_country
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class VanishedDisapearedLoader(DirectoryLoader):
    """
    Journal-level metadata from the "Vanished Journals" project. This is the
    "disapeared" dataset, with many homepage URLs in wayback (web.archive.org).

    CSV headers:
        - Source
        - If Identified by second source
        - Journal Name
        - ISSN
        - E-ISSN
        - URL
        - Publisher
        - blank
        - Language(s)
        - Country
        - society_affiliation
        - other_sci_affiliation
        - Discipline
        - Discipline Group
        - Start Year
        - End Year
        - Last Year Online
        - Actively Publishing
        - Internet Archive Link
        - Verified
        - Comments
        - The Keepers (archived)
        - Archive Link
        - Mikael (1 = agree with Lisa)
    """

    source_slug = "vanished_disapeared"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.vanished_disapeared.filepath))

    def parse_record(self, record) -> Optional[DirectoryInfo]:

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            raw_issn=clean_issn(record["ISSN"]),
            issne=clean_issn(record["E-ISSN"]),
            name=clean_str(record["Journal Name"]),
            publisher=clean_str(record["Publisher"]),
            langs=[lang for lang in [parse_lang(record["Language(s)"])] if lang],
            country=parse_country(record["Country"]),
        )
        homepage = HomepageUrl.from_url(record["Internet Archive Link"])
        if homepage:
            info.homepage_urls.append(homepage)
        homepage = HomepageUrl.from_url(record["Archive Link"])
        if homepage:
            info.homepage_urls.append(homepage)
        return info
