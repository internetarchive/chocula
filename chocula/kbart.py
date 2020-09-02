from chocula.common import KbartLoader, OnixCsvLoader, HathifilesLoader


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


class PkpPlnOnixLoader(OnixCsvLoader):

    source_slug = "pkp_pln"

    def file_path(self) -> str:
        return self.config.pkp_pln.filepath


class HathitrustLoader(HathifilesLoader):

    source_slug = "hathitrust"

    def file_path(self) -> str:
        return self.config.hathitrust.filepath


ALL_CHOCULA_KBART_CLASSES = [
    ClockssKbartLoader,
    LockssKbartLoader,
    PorticoKbartLoader,
    JstorKbartLoader,
    PkpPlnOnixLoader,
    HathitrustLoader,
]
