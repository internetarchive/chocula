#!/usr/bin/env python3

"""
This is a one-off script for pushing ISSN-L fixes to fatcat via the API.

It excpects to have fatcat python libraries available. Run it like:

    export FATCAT_API_AUTH_TOKEN="..."
    ./fix_invalid_issnl.py ~/code/chocula/invalid_fatcat_issnl.tsv

It creates a new editgroup, which you'll need to merge/accept manually.

Defaults to QA API endpoint; edit the file to switch to prod.
"""

import os, sys
import csv

from fatcat_tools import authenticated_api
from fatcat_client import Editgroup, ContainerEntity
from fatcat_client.rest import ApiException

API_ENDPOINT = "https://api.qa.fatcat.wiki/v0"


def run(api, row_iter):

    eg = api.create_editgroup(Editgroup(description=
        "Update or merge containers with invalid (by checksum) ISSN-L. Using the fix_invalid_issnl.py script from chocula repo."))
    print("Editgroup ident: {}".format(eg.editgroup_id))
    for row in row_iter:
        #print(row)
        fixed_issnl = row['fixed_issnl'].strip()
        if not fixed_issnl:
            print("SKIP")
            continue
        assert row['issnl'].strip() != fixed_issnl
        invalid = api.get_container(row['fatcat_ident'])
        assert invalid.state == "active"
        try:
            fixed = api.lookup_container(issnl=row['fixed_issnl'])
        except ApiException as ae:
            if ae.status != 404:
                raise ae
            fixed = None

        if fixed:
            # merge/redirect
            assert fixed.state == "active"
            print("MERGE: {} -> {}".format(invalid.ident, fixed.ident))
            invalid.redirect = fixed.ident
            api.update_container(eg.editgroup_id, invalid.ident,
                ContainerEntity(redirect=fixed.ident))
        else:
            # update in-place with fixed ISSN-L
            print("FIX: {}: {}".format(invalid.ident, fixed_issnl))
            invalid.issnl = fixed_issnl
            api.update_container(eg.editgroup_id, invalid.ident, invalid)

    # intentionally not merging editgroup
    print("Editgroup ident: {}".format(eg.editgroup_id))
    print("DONE")

def main():
    api = authenticated_api(
        API_ENDPOINT,
        # token is an optional kwarg (can be empty string, None, etc)
        token=os.environ.get("FATCAT_API_AUTH_TOKEN"))

    path = sys.argv[1]
    reader = csv.DictReader(open(path), delimiter='\t')
    run(api, reader)

if __name__ == '__main__':
    main()
