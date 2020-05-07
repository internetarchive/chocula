
import sys
from typing import Iterable, Optional
from collections import Counter

from chocula.config import ChoculaConfig
from chocula.database import DirectoryInfo


class DirectoryLoader():

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
            counts['total'] += 1
            info = self.parse_record(record)
            if info:
                status = db.insert_directory(info, cur=cur)
                counts[status] += 1
        cur.close()
        db.db.commit()
        return counts
