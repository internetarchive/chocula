import sys
import csv
import datetime
from typing import Iterable, Optional, Dict, Any, List
from collections import Counter
from dataclasses import dataclass, field

import ftfy

from chocula.util import clean_str, clean_issn, merge_spans
from chocula.config import ChoculaConfig
from chocula.database import DirectoryInfo, IssnDatabase, HomepageUrl


# Portico files have weirdly large field sizes
csv.field_size_limit(1310720)
THIS_YEAR = datetime.date.today().year


class DirectoryLoader:

    source_slug: str = "GENERIC"

    def __init__(self, config: ChoculaConfig):
        self.config = config

    def open_file(self) -> Iterable:
        raise NotImplementedError()

    def parse_record(self, record) -> Optional[DirectoryInfo]:
        raise NotImplementedError()

    def index_file(self, db) -> Counter:
        print(f"##### Loading {self.source_slug}...", file=sys.stderr)
        counts: Counter = Counter()
        cur = db.db.cursor()
        for record in self.open_file():
            counts["total"] += 1
            info = self.parse_record(record)
            if info:
                status = db.insert_directory(info, cur=cur)
                counts[status] += 1
        cur.close()
        db.db.commit()
        return counts


@dataclass
class KbartRecord:
    issnl: Optional[str]
    issne: Optional[str]
    issnp: Optional[str]
    title: Optional[str]
    publisher: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    start_volume: Optional[str]
    end_volume: Optional[str]
    url: Optional[HomepageUrl]
    embargo: Optional[str]
    year_spans: List[Any]


class KbartLoader:

    source_slug: str = "GENERIC"

    def __init__(self, config: ChoculaConfig):
        self.config = config

    def file_path(self) -> str:
        # return self.config.TEMPLATE.filepath)
        raise NotImplementedError()

    def open_file(self) -> Iterable:
        raw_file = open(self.file_path(), "rb").read().decode(errors="replace")
        fixed_file = ftfy.fix_text(raw_file)
        reader = csv.DictReader(fixed_file.split("\n"), delimiter="\t")
        return reader

    def parse_record(self, row: dict, issn_db: IssnDatabase) -> Optional[KbartRecord]:

        issne: Optional[str] = clean_issn(row["online_identifier"] or "")
        issnp: Optional[str] = clean_issn(row["print_identifier"] or "")
        issnl: Optional[str] = None
        if issne:
            issnl = issn_db.issn2issnl(issne)
        if issnp and not issnl:
            issnl = issn_db.issn2issnl(issnp)
        start_year: Optional[int] = None
        end_year: Optional[int] = None
        if row["date_first_issue_online"]:
            start_year = int(row["date_first_issue_online"][:4])
        if row["date_last_issue_online"]:
            end_year = int(row["date_last_issue_online"][:4])
        end_volume = row["num_last_vol_online"]
        # hack to handle open-ended preservation
        if end_year is None and end_volume and "(present)" in end_volume:
            end_year = THIS_YEAR
        record = KbartRecord(
            issnl=issnl,
            issnp=issnp,
            issne=issne,
            title=clean_str(row["publication_title"]),
            publisher=clean_str(row["publisher_name"]),
            url=HomepageUrl.from_url(row["title_url"]),
            embargo=clean_str(row["embargo_info"]),
            start_year=start_year,
            end_year=end_year,
            start_volume=clean_str(row["num_first_vol_online"]),
            end_volume=clean_str(row["num_last_vol_online"]),
            year_spans=[],
        )
        if record.start_volume == "null":
            record.start_volume = None
        if record.end_volume == "null":
            record.end_volume = None
        return record

    def index_file(self, db) -> Counter:
        """
        Transforms a KBART file into a dict of dicts; but basically a list of
        JSON objects, one per journal. KBART files can have multiple rows per
        journal (eg, different year spans), which is why this pass is needed.
        """
        print(f"##### Loading {self.source_slug} KBART...", file=sys.stderr)
        counts: Counter = Counter()
        kbart_dict: Dict[str, KbartRecord] = dict()
        for row in self.open_file():
            counts["total"] += 1

            record = self.parse_record(row, db.issn_db)
            if record is None:
                counts["skip-parse"] += 1
                continue
            elif not record.issnl:
                counts["skip-issnl"] += 1
                continue
            elif record.start_year is None or record.end_year is None:
                counts["partial-missing-years"] += 1
            counts["parsed"] += 1

            existing = kbart_dict.get(record.issnl, record)
            if record.start_year and record.end_year:
                old_spans = existing.year_spans or []
                if not record.start_year <= record.end_year:
                    new_spans = [[record.end_year, record.start_year]]
                else:
                    new_spans = [[record.start_year, record.end_year]]
                record.year_spans = merge_spans(old_spans, new_spans)
            kbart_dict[record.issnl] = record

        counts["unique-issnl"] = len(kbart_dict)
        cur = db.db.cursor()
        for issnl, record in kbart_dict.items():
            info = DirectoryInfo(
                directory_slug=self.source_slug,
                issnl=record.issnl,
                issne=record.issne,
                issnp=record.issnp,
                name=record.title,
                publisher=record.publisher,
                homepage_urls=[],
                extra=dict(year_spans=record.year_spans),
            )
            if record.url:
                info.homepage_urls.append(record.url)
            status = db.insert_directory(info, cur=cur)
            counts[status] += 1
        cur.close()
        db.db.commit()
        return counts
