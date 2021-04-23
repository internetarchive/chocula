from typing import Iterable, Optional
import csv

from chocula.util import (
    clean_str,
    parse_country,
    parse_lang,
)
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class DoajLoader(DirectoryLoader):
    """
    CSV Columns:

    - Journal title
    - Journal URL
    - URL in DOAJ
    - Alternative title
    - Journal ISSN (print version)
    - Journal EISSN (online version)
    - Keywords
    - Languages in which the journal accepts manuscripts
    - Publisher
    - Country of publisher
    - Society or institution
    - Country of society or institution
    - Journal license
    - License attributes
    - URL for license terms
    - Machine-readable CC licensing information embedded or displayed in articles
    - URL to an example page with embedded licensing information
    - Author holds copyright without restrictions
    - Copyright information URL
    - Review process
    - Review process information URL
    - Journal plagiarism screening policy
    - Plagiarism information URL
    - URL for journal's aims & scope
    - URL for the Editorial Board page
    - URL for journal's instructions for authors
    - Average number of weeks between article submission and publication
    - APC
    - APC information URL
    - APC amount
    - Journal waiver policy (for developing country authors etc)
    - Waiver policy information URL
    - Has other fees
    - Other submission fees information URL
    - Preservation Services
    - Preservation Service: national library
    - Preservation information URL
    - Deposit policy directory
    - URL for deposit policy
    - Persistent article identifiers
    - Article metadata includes ORCIDs
    - Journal complies with I4OC standards for open citations
    - Does this journal allow unrestricted reuse in compliance with BOAI?
    - URL for journal's Open Access statement
    - Continues
    - Continued By
    - LCC Codes
    - Subjects
    - DOAJ Seal
    - Added on Date
    - Last updated Date
    - Number of Article Records
    - Most Recent Article Added
    """

    source_slug = "doaj"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.doaj.filepath))

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        # TODO: Subjects, Permanent article identifiers, work_level stuff

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnp=row["Journal ISSN (print version)"],
            issne=row["Journal EISSN (online version)"],
            name=clean_str(row["Journal title"]),
            publisher=clean_str(row["Publisher"]),
            country=parse_country(row["Country of publisher"]),
        )

        lang = parse_lang(row["Languages in which the journal accepts manuscripts"])
        if lang:
            info.langs.append(lang)

        info.extra["as_of"] = self.config.snapshot.date
        if row["DOAJ Seal"]:
            info.extra["seal"] = {"no": False, "yes": True}[row["DOAJ Seal"].lower()]

        if row["Preservation Services"]:
            info.extra["archive"] = [
                a.strip() for a in row["Preservation Services"].split(",") if a.strip()
            ]
        elif row["Preservation Service: national library"]:
            info.extra["archive"] = ["national-library"]

        default_license = row["Journal license"]
        if default_license and default_license.startswith("CC"):
            info.extra["default_license"] = default_license.replace(
                "CC ", "CC-"
            ).strip()

        url = row["Journal URL"]
        if url:
            homepage = HomepageUrl.from_url(row["Journal URL"])
            if homepage:
                info.homepage_urls.append(homepage)
        return info
