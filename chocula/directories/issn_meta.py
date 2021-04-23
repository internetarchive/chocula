from typing import Iterable, Optional
import json

from chocula.util import clean_str, clean_issn, parse_country
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class IssnMetaLoader(DirectoryLoader):
    """
    This is JSON-LD (-ish) scraped from portal.issn.org, filtered down to only
    journals already in the corpus, or matching a couple other criteria.

    Metadata we expect to get:

    - high quality English title
    - URLs
    - country

    TODO: non-english alternative titles
    """

    source_slug = "issn_meta"

    def open_file(self) -> Iterable:
        return open(self.config.issn_meta.filepath, "r")

    def parse_record(self, row) -> Optional[DirectoryInfo]:

        row = json.loads(row)

        info = DirectoryInfo(
            directory_slug=self.source_slug,
        )
        # format is an array of metadata elements
        for el in row:
            if "label" in el and el["@id"].startswith(
                "http://id.loc.gov/vocabulary/countries"
            ):
                value = el["label"]
                if "(State)" in value:
                    value = ""
                if value == "Russia (Federation)":
                    value = "Russia"
                info.country = parse_country(el["label"])
            if not "@type" in el:
                continue
            if el["@type"] == "http://id.loc.gov/ontologies/bibframe/IssnL":
                info.issnl = clean_issn(el["value"])
            if "mainTitle" in el:
                if type(el["mainTitle"]) == list:
                    info.name = clean_str(el["mainTitle"][0])
                else:
                    info.name = clean_str(el["mainTitle"])
                if el.get("format") == "vocabularies/medium#Print":
                    info.issnp = clean_issn(el["issn"])
                elif el.get("format") == "vocabularies/medium#Electronic":
                    info.issne = clean_issn(el["issn"])
            urls = el.get("url", [])
            if isinstance(urls, str):
                urls = [
                    urls,
                ]
            for url in urls:
                homepage = HomepageUrl.from_url(url)
                if homepage:
                    info.homepage_urls.append(homepage)

        return info
