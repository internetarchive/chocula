
from dataclasses import dataclass
from typing import Dict, Optional

import ftfy
import pycountry

################### Utilities

# NOTE: this is a partial list, focusing on non-publisher hosted platforms and
# software frameworks
PLATFORM_MAP = {
    'OJS': 'ojs',
    'BMC': 'bmc',
    'SciELO Brazil': 'scielo',
    'SciELO Argentina': 'scielo',
    'SciELO': 'scielo',
    'SciELO Mexico': 'scielo',
    'SciELO Spain': 'scielo',
    'SciELO Portugal': 'scielo',
    'WordPress': 'wordpress',
    'Sciendo': 'sciendo',
    'Drupal': 'drupal',
    'revues.org': 'openedition',
}

MIMETYPE_MAP = {
    'PDF': 'application/pdf',
    'HTML': 'text/html',
    'XML': 'application/xml',
}

BIG5_PUBLISHERS = [
    'Elsevier',
    'Informa UK (Taylor & Francis)',
    'Springer-Verlag',
    'SAGE Publications',
    'Wiley (Blackwell Publishing)',
    'Wiley (John Wiley & Sons)',
    'Springer (Biomed Central Ltd.)',
    'Springer Nature',
]
COMMERCIAL_PUBLISHERS = [
    'Peter Lang International Academic Publishers',
    'Walter de Gruyter GmbH',
    'Oldenbourg Wissenschaftsverlag',
    'Georg Thieme Verlag KG', # not springer
    'Emerald (MCB UP )',
    'Medknow Publications',
    'Inderscience Enterprises Ltd',
    'Bentham Science',
    'Ovid Technologies (Wolters Kluwer)  - Lippincott Williams & Wilkins',
    'Scientific Research Publishing, Inc',
    'MDPI AG',
    'S. Karger AG',
    'Pleiades Publishing',
    'Science Publishing Group',
    'IGI Global',
    'The Economist Intelligence Unit',
    'Maney Publishing',
    'Diva Enterprises Private Limited',
    'World Scientific',
    'Mary Ann Liebert',
    'Trans Tech Publications',
]
OA_PUBLISHERS = [
    'Hindawi Limited',
    'OMICS Publishing Group',
    'De Gruyter Open Sp. z o.o.',
    'OpenEdition',
    'Hindawi (International Scholarly Research Network)',
    'Public Library of Science',
    'Frontiers Media SA',
    'eLife Sciences Publications, Ltd',
    'MDPI AG',
    'Hindawi (International Scholarly Research Network)',
    'Dove Medical Press',
    'Open Access Text',
]
SOCIETY_PUBLISHERS = [
    'Institute of Electrical and Electronics Engineers',
    'Institution of Electrical Engineers',
    'Association for Computing Machinery',
    'American Psychological Association',
    'IOS Press',
    'IOP Publishing',
    'American Chemical Society',
    'Royal Society of Chemistry (RSC)',
    'American Geophysical Union',
    'American College of Physicians',
    'New England Journal of Medicine',
    'BMJ',
    'RCN Publishing',
    'International Union of Crystallography',
    'Portland Press',
    'ASME International',
]
UNI_PRESS_PUBLISHERS = [
    'Cambridge University Press',
    'Oxford University Press',
    'The University of Chicago Press',
    'MIT Press',
]
ARCHIVE_PUBLISHERS = [
    'JSTOR',
    'Portico',
]
REPOSITORY_PUBLISHERS = [
    'PERSEE Program',
    'Social Science Electronic Publishing',
    'CAIRN',
    'CSIRO Publishing',
]
OTHER_PUBLISHERS = [
    'African Journals Online',
    'Smithsonian Institution Biodiversity Heritage Library',
    'Canadian Science Publishing',
    'Philosophy Documentation Center',
    'Project MUSE',
]

def parse_lang(s):
    if not s or s in ('Not applicable', 'Multiple languages', 'Unknown'):
        return None
    try:
        if len(s) == 2:
            lang = pycountry.languages.get(alpha2=s.lower())
        elif len(s) == 3:
            lang = pycountry.languages.get(alpha3=s.lower())
        else:
            lang = pycountry.languages.get(name=s)
        return lang.alpha2.lower()
    except KeyError:
        return None
    except AttributeError:
        return None

def parse_country(s):
    if not s or s in ('Unknown'):
        return None
    try:
        if len(s) == 2:
            country = pycountry.countries.get(alpha2=s.lower())
        else:
            country = pycountry.countries.get(name=s)
    except KeyError:
        return None
    if country:
        return country.alpha_2.lower()
    else:
        return None

def parse_mimetypes(val):
    # XXX: multiple mimetypes?
    if not val:
        return
    mimetype = None
    if '/' in val:
        mimetype = val
    else:
        mimetype = MIMETYPE_MAP.get(val)
    if not mimetype:
        return None
    return [mimetype]

def gaps_to_spans(first, last, gaps):
    if not gaps:
        return [[first, last]]
    if not (last >= first and max(gaps) < last and min(gaps) > first):
        # years seem mangled? will continue though
        print("mangled years: {}".format((first, last, gaps)), file=sys.stderr)
    full = list(range(first, last+1))
    for missing in gaps:
        full.remove(missing)
    spans = []
    low = None
    last = None
    for year in full:
        if not low:
            low = year
            last = year
            continue
        if year != last+1:
            spans.append([low, last])
            low = year
            last = year
        last = year
    if low:
        spans.append([low, last])
    return spans

def test_gaps():
    assert gaps_to_spans(1900, 1900, None) == \
        [[1900, 1900]]
    assert gaps_to_spans(1900, 1903, None) == \
        [[1900, 1903]]
    assert gaps_to_spans(1900, 1902, [1901]) == \
        [[1900, 1900], [1902, 1902]]
    assert gaps_to_spans(1950, 1970, [1955, 1956, 1965]) == \
        [[1950, 1954], [1957, 1964], [1966, 1970]]

def merge_spans(old, new):
    if not new:
        return old
    if not old:
        old = []
    old.extend(new)
    years = set()
    for span in old:
        for y in range(span[0], span[1]+1):
            years.add(y)
    if not years:
        return []
    spans = []
    start = None
    last = None
    todo = False
    for y in sorted(list(years)):
        if start == None:
            # very first
            start = y
            last = y
            todo = True
            continue
        if y == last + 1:
            # span continues
            last = y
            todo = True
            continue
        # a gap just happened!
        spans.append([start, last])
        start = y
        last = y
        todo = True
    if todo:
        spans.append([start, last])
    return spans

def test_merge_spans():
    assert merge_spans([[5, 10]], [[10, 20]]) == \
        [[5, 20]]
    assert merge_spans([[5, 9]], [[10, 20]]) == \
        [[5, 20]]
    assert merge_spans([[5, 11]], [[10, 20]]) == \
        [[5, 20]]
    assert merge_spans([], []) == \
        []
    assert merge_spans([[9, 11]], []) == \
        [[9,11]]
    assert merge_spans([[2000, 2000]], [[1450, 1900]]) == \
        [[1450, 1900], [2000, 2000]]


def unquote(s: str) -> str:
    if s.startswith('"') or s.startswith("'"):
        s = s[1:]
    if s.endswith('"') or s.endswith("'"):
        s = s[:-1]
    if s.endswith('.'):
        s = s[:-1]
    return s.strip()


def clean_str(s: Optional[str]) -> Optional[str]:
    """
    Takes a generic string and "cleans" it:

    - strips whitespace
    - de-mangles unicode
    - strips HTML tags
    - transforms HTML entities to unicode characters
    - removes leading and trailing

    This version of the function is pretty aggressive; it is intended for
    journal titles, publisher names, etc, not things like article titles.
    """
    if not s:
        return None
    s = unquote(ftfy.fix_text(s))
    return s or None

def test_clean_str():
    assert clean_str("") is None
    assert clean_str(" ") is None
    assert clean_str("" "") is None
    assert clean_str(" Bloody work.") == "Bloody work"



def clean_issn(s: str) -> Optional[str]:
    s = s.strip().upper()
    if len(s) == 8:
        s = s[:4] + "-" + s[4:]
    if len(s) != 9 or s[4] != "-":
        return None
    return s

def test_clean_issn():
    assert clean_issn("1234-5678") == "1234-5678"
    assert clean_issn(" 12345678") == "1234-5678"
    assert clean_issn("123445678") == None
