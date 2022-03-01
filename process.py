#!/usr/bin/env python3

import argparse
import json
import sys

from datetime import date
from datetime import datetime


class Vaers(object):
    def __init__(self, year, vax=None):
        self.data = json.load(open(str(year) + "VAERS.json", encoding="latin1"))
        self.vax = vax
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

    def vax_counts(self):
        print("-" * 80)
        if self.vax:
            print(
                f"Vaccine counts for vaccines matching '{self.vax}' for {self.year} data"
            )
        else:
            print(f"Vaccine counts for {self.year} data")
        print()
        print_count_key(self.data, "VAX_NAME", match=self.vax)
        print("-" * 80)

    def vax_symptoms(self, min_lim=25, min_pct=1.0, filters=[], dedupe={}):
        vaxes = {}
        for vid in self.data:
            vax = self.data[vid]["VAX_NAME"]
            if self.vax and self.vax.lower() not in vax.lower():
                continue
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
        print("-" * 80)
        header = "Symptoms occurence per vaccine"
        if self.vax:
            header += f" for vaccines matching '{self.vax}'"
        header += f" for {self.year} data.\n"
        header += f"Minimum symptom count: {min_lim}  Minimum percent: {min_pct:.1f}%  Filters: [{', '.join(filters)}]  Dedupe: {dedupe}"
        print(header)
        print()
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
        print("-" * 80)

    def get_symptom_texts(self, text="inappropriate age"):
        symptoms = {}
        total = 0
        for vid in self.data:
            for symptom in self.data[vid]["SYMPTOMS"]:
                if (
                    self.vax is not None
                    and self.vax.lower() not in self.data[vid]["VAX_NAME"].lower()
                ):
                    continue
                if text.lower() in symptom.lower():
                    if symptom in symptoms:
                        symptoms[symptom] += 1
                    else:
                        symptoms[symptom] = 1
        print("-" * 80)
        if self.vax:
            print(
                f"Symptoms containing '{text}' reported for vaccines matching '{self.vax}' from {self.year} data"
            )
        else:
            print(
                f"Symptoms containing '{text}' reported for vaccines from {self.year} data"
            )
        print()
        for symptom in sorted(symptoms, key=lambda x: symptoms[x], reverse=True):
            print(f"{symptom}: {symptoms[symptom]}")
            total += symptoms[symptom]
        print()
        print(f"Total: {total}")
        print("-" * 80)


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
        if match is not None and match.lower() not in val.lower():
            continue
        total += 1
        count[val] = count.get(val, 0) + 1
    return (count, total)


def print_count_key(src, key, match=None):
    count, total = count_key(src, key, match)
    for k, v in sorted(count.items(), reverse=True, key=lambda x: x[1]):
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
    output_parser = argparse.ArgumentParser(add_help=False)
    output_group = output_parser.add_argument_group("output arguments")

    output_group.add_argument(
        "-c",
        "--count",
        default=False,
        action="store_true",
        help="print COVID-19 vaccine counts",
    )
    output_group.add_argument(
        "-g",
        "--graph",
        default=False,
        action="store_true",
        help="graph number of VAERS reports",
    )
    output_group.add_argument(
        "-s",
        "--symptoms",
        default=False,
        action="store_true",
        help="print reported symptoms for each vaccine",
    )
    output_group.add_argument(
        "-t",
        "--text",
        default=None,
        action="store",
        help="print symptoms that contain TEXT",
    )

    all_parser = argparse.ArgumentParser(
        parents=[output_parser],
        description="Process VAERS data",
        epilog="At least one output argument is required",
    )
    all_parser.add_argument(
        "-v",
        "--vaccine",
        default=None,
        action="store",
        help="vaccine type",
    )
    all_parser.add_argument(
        "-y",
        "--year",
        default=date.today().year,
        action="store",
        help="year of data file to use",
    )

    output_args, _ = output_parser.parse_known_args()
    args = all_parser.parse_args()

    # Skip loading data and processing if no output will be given
    if len([x for x in vars(output_args).values() if x]) == 0:
        print("An output argument is required.")
        all_parser.print_help()
        sys.exit(0)

    vaers = Vaers(args.year, vax=args.vaccine)

    if args.count:
        vaers.vax_counts()
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
