#!/usr/bin/env python3

"""
This is a helper script to convert ONIX XML (eg, from Scholar's Portal) to Onix CSV format.

Rough XML schema:

    oph:HoldingsList
      oph:HoldingsRecord (many)
        oph:NotificationType text "00" (?)
        oph:ResourceVersion
            oph:ResourceVersionIdentifier
                oph:ResourceVersionIDType "07" is ISSN?
                oph:IDValue
            oph:Title
                oph:TitleText journal title
            oph:Publisher
                oph:PublisherName publisher name
            oph:OnlinePackage
                oph:PackageDetail (multiple)
                    oph:Coverage
                        oph:CoverageDescriptionLevel "03"
                        oph:FixedCoverage
                            oph:Release (multiple)
                                oph:Enumeration
                                    oph:Level1
                                        oph:Unit "Volume"
                                        oph:Number volume number
                                    oph:Level2
                                        oph:Unit "Issue"
                                        oph:Number issue number
                                    oph:NominalDate
                                        oph:DateFormat "01"
                                        oph:Date partial date, eg "197803"
    
                oph:PreservationStatus
                    oph:PreservationStatusCode "05"
                oph:VerificationStatus "01"

ONIX CSV columns:

    ISSN
    Title
    Publisher
    Url
    Vol
    No
    Published
    Deposited
"""

import sys
import csv
import argparse
import xml.etree.ElementTree as ET
from typing import List, Any, Dict, AnyStr, Optional


oph = "{http://www.editeur.org/onix/serials/SOH}"
xml_ns = {
    "oph": "http://www.editeur.org/onix/serials/SOH",
}

def fix_issn(raw: str) -> Optional[str]:
    if len(raw) == 9:
        return raw
    if len(raw) == 8:
        return f"{raw[:4]}-{raw[4:8]}"
    return None

def fix_date(raw: str) -> str:
    if len(raw) == 6 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}"
    return raw

def fix_str(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return raw.strip().replace('\n', ' ')

def resource_to_rows(resource) -> List[dict]:
    rows = []
    base = dict()
    if resource.find('oph:ResourceVersionIdentifier/oph:ResourceVersionIDType', xml_ns).text != "07":
        return []
    base['ISSN'] = fix_issn(resource.find('oph:ResourceVersionIdentifier/oph:IDValue', xml_ns).text)
    base['Title'] = fix_str(resource.find('oph:Title/oph:TitleText', xml_ns).text)
    if not base['Title']:
        return []
    base['Publisher'] = fix_str(resource.find('oph:Publisher/oph:PublisherName', xml_ns).text)
    base['Url'] = ''
    base['Deposited'] = ''
    for package in resource.findall('oph:OnlinePackage/oph:PackageDetail', xml_ns):
        if package.find('oph:Coverage/oph:CoverageDescriptionLevel', xml_ns).text != "03":
            continue
        if package.find('oph:VerificationStatus', xml_ns).text != "01":
            continue
        if package.find('oph:PreservationStatus/oph:PreservationStatusCode', xml_ns).text != "05":
            continue
        for release in package.findall('oph:Coverage/oph:FixedCoverage/oph:Release', xml_ns):
            row = dict()
            if release.find('oph:Enumeration/oph:Level1/oph:Unit', xml_ns).text != "Volume":
                continue
            row['Vol'] = release.find('oph:Enumeration/oph:Level1/oph:Number', xml_ns).text
            if release.find('oph:Enumeration/oph:Level2/oph:Unit', xml_ns).text != "Issue":
                continue
            row['No'] = release.find('oph:Enumeration/oph:Level2/oph:Number', xml_ns).text
            if release.find('oph:NominalDate/oph:Date', xml_ns) == None:
                continue
            row['Published'] = fix_date(release.find('oph:NominalDate/oph:Date', xml_ns).text)
            row.update(base)
            rows.append(row)
    return rows

def onix_xml_to_csv(xml_input_file, csv_output_file):

    elem_iter = ET.iterparse(xml_input_file, ["start", "end"])

    fieldnames = ['ISSN', 'Title', 'Publisher', 'Url', 'Vol', 'No', 'Published', 'Deposited']
    writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames)
    writer.writeheader()

    root = None
    for (event, element) in elem_iter:
        #print(element, file=sys.stderr)
        if not root and event == "start":
            root = element
            continue
        if not (element.tag == f"{oph}ResourceVersion" and event == "end"):
            continue
        for row in resource_to_rows(element):
            writer.writerow(row)
        element.clear()
        root.clear()

def main() -> None:  # pragma no cover
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="ONIX XML to JSON",
        usage="%(prog)s <xml_input_file> <csv_output_file>",
    )
    parser.add_argument("xml_input_file", type=argparse.FileType('r'))
    parser.add_argument("csv_output_file", type=argparse.FileType('w'))

    args = parser.parse_args()

    onix_xml_to_csv(args.xml_input_file, args.csv_output_file)


if __name__ == "__main__":  # pragma no cover
    main()
