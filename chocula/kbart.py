
from typing import List, Any
from chocula.common import KbartLoader


class ClockssKbartLoader(KbartLoader):

    source_slug = "clockss"

    def file_path(self) -> str:
        return self.config.clockss.filepath


class LockssKbartLoader(KbartLoader):

    source_slug = "lockss"

    def file_path(self) -> str:
        return self.config.lockss.filepath


class PorticoKbartLoader(KbartLoader):

    source_slug = "portico"

    def file_path(self) -> str:
        return self.config.portico.filepath
 

class JstorKbartLoader(KbartLoader):

    source_slug = "jstor"

    def file_path(self) -> str:
        return self.config.jstor.filepath


ALL_CHOCULA_KBART_CLASSES = [
    ClockssKbartLoader,
    LockssKbartLoader,
    PorticoKbartLoader,
    JstorKbartLoader,
]
