import sys
import json

for line in sys.stdin:
    if not line.strip():
        continue
    record = json.loads(line)["@graph"]
    issnl = None
    for el in record:
        if el.get("@type") == "http://id.loc.gov/ontologies/bibframe/IssnL":
            issnl = el["value"]
            break
    if issnl:
        print("\t".join((issnl, json.dumps(record, sort_keys=True))))
