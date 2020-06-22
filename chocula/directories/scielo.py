from typing import Iterable, Optional
import json

from chocula.util import clean_str, clean_issn
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class ScieloLoader(DirectoryLoader):

    source_slug = "scielo"

    def open_file(self) -> Iterable:
        return open(self.config.scielo.filepath)

    def parse_record(self, line) -> Optional[DirectoryInfo]:
        record = json.loads(line)
        extra = dict(
            status=clean_str(record.get("current_status")),
            first_year=record.get("first_year"),
            collection=record.get("collection_acronym"),
        )
        for k in list(extra.keys()):
            if extra[k] is None:
                extra.pop(k)
        country: Optional[str] = None
        if record["publisher_country"] and len(record["publisher_country"][0]) == 2:
            country = record["publisher_country"][0].lower()
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issne=clean_issn(record.get("electronic_issn") or ""),
            issnp=clean_issn(record.get("print_issn") or ""),
            custom_id=clean_str(record.get("scielo_issn")),
            name=clean_str(record.get("fulltitle")),
            publisher=clean_str((record.get("publisher_name") or [""])[0]),
            abbrev=clean_str(record["abbreviated_iso_title"]),
            platform="scielo",
            langs=list(filter(lambda s: len(s) == 2, record["languages"])),
            country=country,
            extra=extra,
        )
        if record["url"]:
            homepage = HomepageUrl.from_url(record["url"])
            if homepage:
                info.homepage_urls.append(homepage)
        return info
