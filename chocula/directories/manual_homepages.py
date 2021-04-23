import csv
from typing import Iterable, Optional

from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class ManualHomepageLoader(DirectoryLoader):

    source_slug = "manual_homepages"

    def open_file(self) -> Iterable:
        return csv.DictReader(
            open(self.config.manual_homepages.filepath),
            delimiter="\t",
        )

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        """
        Most of this metadata comes from chocula/fatcat; we are only interested
        in the homepage URLs.

        The "corrected titles" have been manually entered into fatcat directly.

        CSV columns:
        - issnl
        - issnp
        - issne
        - name
        - corrected title
        - publisher
        - country
        - lang
        - release_count
        - Homepage URL
        - Inactive
        """

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnl=record["issnl"],
        )
        url = record["Homepage URL"]
        if url is None or url.lower() == "unknown" or len(url) < 4:
            return None
        homepage = HomepageUrl.from_url(url)
        if homepage:
            info.homepage_urls.append(homepage)
        if homepage is None:
            return None
        return info
