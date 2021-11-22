from chocula.directories.crossref import CrossrefLoader
from chocula.directories.doaj import DoajLoader
from chocula.directories.entrez import EntrezLoader
from chocula.directories.ezb import EzbLoader
from chocula.directories.gold_oa import GoldOALoader
from chocula.directories.norwegian import NorwegianLoader
from chocula.directories.openapc import OpenAPCLoader
from chocula.directories.road import RoadLoader
from chocula.directories.sherpa_romeo import SherpaRomeoLoader
from chocula.directories.sim import SimLoader
from chocula.directories.scielo import ScieloLoader
from chocula.directories.szczepanski import SzczepanskiLoader
from chocula.directories.wikidata import WikidataLoader
from chocula.directories.manual_homepages import ManualHomepageLoader
from chocula.directories.zdb_fize import ZdbFizeLoader
from chocula.directories.vanished_disapeared import VanishedDisapearedLoader
from chocula.directories.vanished_inactive import VanishedInactiveLoader
from chocula.directories.issn_meta import IssnMetaLoader
from chocula.directories.australian_era import AustralianEraLoader
from chocula.directories.awol import AwolLoader
from chocula.directories.mag import MagLoader
from chocula.directories.openalex import OpenAlexLoader

# sort order roughly results in metadata prioritization
ALL_CHOCULA_DIR_CLASSES = [
    IssnMetaLoader,
    ManualHomepageLoader,
    ScieloLoader,
    DoajLoader,
    CrossrefLoader,
    EntrezLoader,
    EzbLoader,
    GoldOALoader,
    NorwegianLoader,
    AustralianEraLoader,
    SzczepanskiLoader,
    WikidataLoader,
    AwolLoader,
    VanishedDisapearedLoader,
    VanishedInactiveLoader,
    OpenAPCLoader,
    RoadLoader,
    SherpaRomeoLoader,
    SimLoader,
    ZdbFizeLoader,
    MagLoader,
    OpenAlexLoader,
]
