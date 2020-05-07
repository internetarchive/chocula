
from typing import Iterable, Optional
import csv

from chocula.util import clean_str, parse_lang, parse_country
from chocula.common import DirectoryLoader
from chocula.database import DirectoryInfo, HomepageUrl


class NorwegianLoader(DirectoryLoader):
    """
    CSV Columns (2020 file):

        NSD tidsskrift_id
        Original title
        International title
        Print ISSN
        Online ISSN
        Open Access
        NPI Academic Discipline
        NPI Scientific Field
        Level 2020
        Level 2019
        Level 2018
        Level 2017
        Level 2016
        Level 2015
        Level 2014
        Level 2013
        Level 2012
        Level 2011
        Level 2010
        Level 2009
        Level 2008
        Level 2007
        Level 2006
        Level 2005
        Level 2004
        itar_id
        NSD forlag_id
        Publishing Company
        Publisher
        Country of publication
        Language
        Conference Proceedings
        Established
        Ceased
        URL

    """

    source_slug = "norwegian"

    def open_file(self) -> Iterable:
        return csv.DictReader(open(self.config.NORWEGIAN_FILE, encoding="ISO-8859-1"), delimiter=";")

    def parse_record(self, row) -> Optional[DirectoryInfo]:
        info = DirectoryInfo(
            directory_slug=self.source_slug,
            issnp=row['Print ISSN'],
            issne=row['Online ISSN'],
            country=parse_country(row['Country of publication']),
            name=clean_str(row.get('International title')),
            langs=[l for l in [parse_lang(row['Language'])] if l],
        )

        info.extra['norwegian'] = dict(as_of=self.config.NORWEGIAN_DATE)
        if row['Level 2019']:
            info.extra['norwegian']['level'] = int(row['Level 2019'])

        if row['Original title'] != row['International title']:
            info.original_name = clean_str(row['Original title'])

            identifier=row['NSD tidsskrift_id'],
            publisher=row['Publisher'],

        url = HomepageUrl.from_url(row['URL'])
        if url:
            info.homepage_urls.append(url)

        return info
