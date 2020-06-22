import sys
from typing import Iterable, Optional, Dict, Any
import csv

import ftfy

from chocula.util import clean_str, parse_country
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo


class SherpaRomeoLoader(DirectoryLoader):
    """
    CSV Columns:

        #RoMEO Record ID,Publisher,Policy Heading,Country,RoMEO colour,Published Permission,Published Restrictions,Published Max embargo,Accepted Prmission,Accepted Restrictions,Accepted Max embargo,Submitted Permission,Submitted Restrictions,Submitted Max embargo,Open Access Publishing,Record Status,Updated

        #Journal Title,ISSN,ESSN,URL,RoMEO Record ID,Updated

    """

    source_slug = "sherpa_romeo"
    sherpa_policies: Dict[str, Any] = dict()

    def open_file(self) -> Iterable:

        # first load policies
        print("##### Loading SHERPA/ROMEO policies...", file=sys.stderr)
        fixed_policy_file = ftfy.fix_file(
            open(self.config.sherpa_romeo_policies_simple.filepath, "rb")
        )
        policy_reader = csv.DictReader(fixed_policy_file)
        for row in policy_reader:
            self.sherpa_policies[row["RoMEO Record ID"]] = row

        # then open regular file
        raw_file = (
            open(self.config.sherpa_romeo_journals_simple.filepath, "rb")
            .read()
            .decode(errors="replace")
        )
        fixed_file = ftfy.fix_text(raw_file)
        return csv.DictReader(fixed_file.split("\n"))

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        # super mangled :(

        row.update(self.sherpa_policies[row["RoMEO Record ID"]])

        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnp=row["ISSN"],
            issne=row["ESSN"],
            name=clean_str(row["Journal Title"]),
            publisher=clean_str(row["Publisher"]),
            country=parse_country(row["Country"]),
            custom_id=row["RoMEO Record ID"],
        )

        if row["RoMEO colour"]:
            info.extra["sherpa_romeo"] = dict(color=row["RoMEO colour"])

        return info
