
content comes from martin's scraping tool

plan:
- filter down to in-scope ISSNs
    => journal (or synonym/translation) in title?
    => join with existing ISSN-Ls
- key metadata
    => country
    => language
    => URL
    => correct title
    => print/electric ISSNs

Total size:

    xzcat data.ndjson.xz | wc -l
    2,141,737

    xzcat data.ndjson.xz | rg -i journal | wc -l
    136,696

    xzcat data.ndjson.xz | rg -i '(Online)' | wc -l
    285,292

Other in-scope keywords: "IEEE", "Proceedings"

Blocklist: "Annual report", "Directory of ...", "Business directory ..."

JSON linked data format:

    @graph

        mainTitle: sometimes an array (with different character sets)

Transform to TSV with ISSN-L as first column, JSON of "@graph" as second column:

    # was going to paste but decided not to do it this way
    #xzcat data.ndjson.xz | jq '."@graph"[] | select(."@type" == "http://id.loc.gov/ontologies/bibframe/IssnL") | .value' -r > issnl_col.txt
    #xzcat data.ndjson.xz | jq '."@graph"' > graph_col.txt

    xzcat data.ndjson.xz | rg -v "org.elasticsearch.client.transport.NoNodeAvailableException" | python3 issnl_prefix.py | pv -l | sort > issn_meta_issnl_prefix.tsv
    => 2.14M
    => NOTE: terminated from json.decoder.JSONDecodeError: Expecting ':' delimiter

    cat data/container_export.json | jq .issnl -r | rg -v ^null | sort -u > fatcat_issnl.txt

    # was: cat issn_meta_issnl_prefix.tsv | rg -i "journal " > issn_meta.journal.tsv
    cat issn_meta_issnl_prefix.tsv | rg -i "journal " | rg '"url":' | rg -iv "magazine" > issn_meta.journal.tsv
    join -t $'\t' fatcat_issnl.txt issn_meta_issnl_prefix.tsv > issn_meta.fatcat.tsv
    cat issn_meta.journal.tsv issn_meta.fatcat.tsv | cut -f2 | sort -u > issn_meta.filtered.json

    wc -l fatcat_issnl.txt issn_meta.*.json
        147973 fatcat_issnl.txt
        216673 issn_meta.fatcat.json
        277076 issn_meta.filtered.json
        136696 issn_meta.journal.json

    cat issn_meta.journal.tsv issn_meta.fatcat.tsv | cut -f1 | sort -u | wc -l
    => 197,724

Original "journal" filter would be about 50k new journals. With some narrower
filters (no "magazine", require a URL defined):

    join -t $'\t' -v 2 fatcat_issnl.txt issn_meta_issnl_prefix.tsv | rg -i "journal " | rg '"url":' | rg -iv "magazine" > issn_meta.new.tsv

    wc -l issn_meta.new.tsv
    12819 issn_meta.new.tsv

    cut -f1 issn_meta.new.tsv | sort -u | wc -l
    11773

