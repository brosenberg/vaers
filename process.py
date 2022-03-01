#!/usr/bin/env python3

import argparse
import json
import sys

from datetime import date
from datetime import datetime


class Vaers(object):
    def __init__(self, year):
        self.data = json.load(open(str(year) + "VAERS.json", encoding="latin1"))
        self.year = year

    def print_vaccine_types(self, ids):
        vaccines = {}
        total = len(ids)
        for i in ids:
            vaccine = self.data[i]["VAX_NAME"]
            vaccines[vaccine] = vaccines.get(vaccine, 0) + 1
        for k, v in sorted(vaccines.items(), key=lambda x: x[1]):
            print(f"{k}: {v} ({100*v/total:.2f}%)")
        print()
        print(f"Total: {total}")

    def vax_symptoms(self, min_lim=25, min_pct=1.0, filters=[], dedupe={}):
        vaxes = {}
        for vid in self.data:
            vax = self.data[vid]["VAX_NAME"]
            if vax not in vaxes:
                vaxes[vax] = {}
            vaxes[vax]["EVENTS"] = vaxes[vax].get("EVENTS", 0) + 1
            for symptom in self.data[vid]["SYMPTOMS"]:
                symptom = symptom.lower()
                if filters and symptom not in filters:
                    continue
                if symptom in dedupe:
                    symptom = dedupe[symptom]
                vaxes[vax][symptom] = vaxes[vax].get(symptom, 0) + 1
        print(
            f"Symptoms occurence per vaccine for {self.year} data. Minimum symptom count: {min_lim}  Minimum percent: {min_pct}  Filters: [{', '.join(filters)}]  Dedupe: {dedupe}"
        )
        for vax in sorted(vaxes, key=lambda x: vaxes[x]["EVENTS"], reverse=True):
            print(f"{vax} - Count: {vaxes[vax]['EVENTS']}")
            other = 0
            for k, v in sorted(vaxes[vax].items(), key=lambda x: x[1], reverse=True):
                if k == "EVENTS":
                    continue
                pct = 100 * v / vaxes[vax]["EVENTS"]
                if v >= min_lim and pct >= min_pct:
                    print(f"{k}: {v} ({pct:0.1f}%)")
                else:
                    other += v
            if other:
                print(
                    f"Below Threshold (Min Count:{min_lim}  Min Percent:{min_pct:0.1f}%): {other}"
                )
            print()

    def get_symptom_texts(self, text="inappropriate age"):
        symptoms = {}
        for vid in self.data:
            for symptom in self.data[vid]["SYMPTOMS"]:
                if text in symptom:
                    print(symptom)


def find_keys_ret_id(src, keys, match):
    ids = []
    match = match.lower()
    for elem in src:
        for key in keys:
            if match in src[elem][key].lower():
                ids.append(elem)
    return ids


def grep_key(src, key, match, display=False):
    total = 0
    match = match.lower()
    for elem in src:
        if match in src[elem][key].lower:
            total += 1
            if display:
                print(src[elem][key])
    print()
    print(f"Total: {total}")


def count_key(src, key, match=None):
    count = {}
    total = 0
    for elem in src:
        val = src[elem][key]
        if match is not None and match not in val:
            continue
        total += 1
        count[val] = count.get(val, 0) + 1
    return (count, total)


def print_count_key(src, key, match=None):
    count, total = count_key(src, key, match)
    for k, v in sorted(count.items(), key=lambda x: x[1]):
        print(f"{k}: {v} ({100*v/total:.2f}%)")
    print()
    print(f"Total: {total}")


def print_fully_vaxed():
    print(
        """https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-total-admin-rate-total
13aug2021
Unknown2dose 94606 (0.06%)
Janssen 13634118 (8.13%)
Moderna 64113369 (38.23%)
Pfizer 89857077 (53.58%)
Total 167699170

20aug2021
Unknown2dose 93910 (0.06%)
Janssen 13849390 (8.17%)
Moderna 64487327 (38.02%)
Pfizer 91162246 (53.75%)
Total 169592873
"""
    )


def find_strokes(vaers):
    stroke_ids = find_keys_ret_id(
        vaers.symptoms,
        SYMPTOMS,
        "stroke",
    )
    vaers.print_vaccine_types(stroke_ids)


def vaccine_counts(vaers):
    print_count_key(vaers.data, "VAX_NAME", match="COVID")


def graph_reports(vaers):
    import matplotlib
    import matplotlib.pyplot

    count = count_key(vaers.data, "RECVDATE")[0]
    dates = matplotlib.dates.date2num(
        [datetime.strptime(x, "%m/%d/%Y") for x in count.keys()]
    )
    values = list(count.values())
    matplotlib.pyplot.plot_date(dates, values, ls="-")
    matplotlib.pyplot.show()


def main():
    parser = argparse.ArgumentParser(description="Process VAERS data")
    parser.add_argument(
        "-c",
        "--count",
        default=False,
        action="store_true",
        help="print COVID-19 vaccine counts",
    )
    parser.add_argument(
        "-g",
        "--graph",
        default=False,
        action="store_true",
        help="graph number of VAERS reports",
    )
    parser.add_argument(
        "-s",
        "--symptoms",
        default=False,
        action="store_true",
        help="print reported symptoms for each vaccine",
    )
    parser.add_argument(
        "-t",
        "--text",
        default=None,
        action="store",
        help="print symptoms that contain TEXT",
    )
    parser.add_argument(
        "-y",
        "--year",
        default=date.today().year,
        action="store",
        help="year of data file to use",
    )

    args = parser.parse_args()
    vaers = Vaers(args.year)

    if args.count:
        vaccine_counts(vaers)
    if args.graph:
        graph_reports(vaers)
    if args.symptoms:
        vaers.vax_symptoms(
            min_lim=25,
            min_pct=0,
            dedupe={
                "sars-cov-2 test positive": "covid-19",
                "covid-19 pneumonia": "covid-19",
            },
        )
    if args.text:
        vaers.get_symptom_texts(args.text)


if __name__ == "__main__":
    main()
