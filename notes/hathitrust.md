
Download: <https://www.hathitrust.org/hathifiles>
Schema: <https://www.hathitrust.org/hathifiles_description>

Munging/filtering huge file to just serials:

    zcat hathi_full_20200801.txt.gz | rg '\tSE\t' | rg '\t\d\d\d\d-\d\d\d.\t' | pv -l > hathi_full_20200801_serials.txt
    => 2.65M 0:00:50 [53.1k/s]

    cut -f10 hathi_full_20200801_serials.txt | sort -u | wc -l
    => 102,008

Wow, that is a lot of coverage! If true.

Columns we would be interested in:

- 2 access (allow=bright, deny=dark)
- 5 description
- 10 issn ("multiple values separated by comma")
- 12 title (if translated, separated by equals or slash)
- 13 imprint (publisher and year; often "publisher, year")
- 17 rights_date_used (year; 9999=unknown)
- 19 lang (MARC format)

Inspect "extent" (volumes/years), ISSN, title:

    shuf -n10 hathi_full_20200801_serials.txt | cut -f2,5,10,12,13,17,19

If we did, eg, onix CSV output, would want:

- ISSN
- Title
- Publisher
- Url
- Vol
- No
- Published
- Deposited

KBART directory fields:

- issnl
- title
- publisher
- year
- volume
- url

Note: could extract some bounds on publication (start date, end date, or both)
from the publisher field

If we trust this metadata, it is going to add some 90k container entities to
fatcat, with very partial metadata. Likely we should at least pull in ISSN
portal (scraped) metadata at the same time.

TODO:
- year ranges (eg, 1976-1978 instead of just the rights_date_used=1978)
- not going to create new 'journal' DB rows if only hathitrust metadata. should expand ISSN metadata for this purpose later
