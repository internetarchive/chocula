
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
from chocula.directories.szczepanski import SzczepanskiLoader
from chocula.directories.wikidata import WikidataLoader

ALL_CHOCULA_DIR_CLASSES = [
    CrossrefLoader, DoajLoader, EntrezLoader,EzbLoader, GoldOALoader,
    NorwegianLoader, OpenAPCLoader, RoadLoader, SherpaRomeoLoader,
    SzczepanskiLoader, WikidataLoader, SimLoader,
]
