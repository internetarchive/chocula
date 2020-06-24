
Original source: <https://isaw.nyu.edu/publications/awol-index/>

Copyright statement:

    The production and publication of The AWOL Index contributes significant
    additional value both to the content itself and to its presentation and
    utility. This new intellectual property is covered by copyright (2015, New
    York University). The full content of The AWOL Index, both in HTML and JSON
    formats, is published under the terms of a Creative Commons
    Attribution-ShareAlike 4.0 International License .

Extracting ISSN-L, Title, URL from this corpus.

Commands:

    unzip awol-index-json.zip
    fd -I .json json/ | parallel cat {} | jq . -c | pv -l > awol-index-combined.json
    cat awol-index-combined.json | rg '"is_part_of":null' > awol-index-top.json
    cat awol-index-top.json | rg '"issn":' > awol-index-top-issn.json

    wc -l awol-index-combined.json awol-index-top.json awol-index-top-issn.json
    52006 awol-index-combined.json
     1302 awol-index-top.json
      503 awol-index-top-issn.json

    rg '"issn":' awol-index-top.json | wc -l
    503

    cat awol-index-combined.json | jq .identifiers.issn.generic -c | rg -v ^null | sort -u | wc -l
    753

    cat awol-index-top.json | jq .identifiers.issn.generic -c | rg -v ^null | sort -u | wc -l
    486

    cat awol-index-top-issn.json | jq .identifiers.issn.generic -c | rg -v ^null | sort -u | wc -l
    486

