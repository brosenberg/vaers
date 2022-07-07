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

    def vax_lots(self):
        vaxes = {}
        for vid in self.data:
            vax = self.data[vid]["VAX_NAME"]
            if self.vax and self.vax.lower() not in vax.lower():
                continue
            if vax not in vaxes:
                vaxes[vax] = {"Lots": {}, "Total": 0}
            lot = self.data[vid]["VAX_LOT"]
            if lot not in vaxes[vax]["Lots"]:
                vaxes[vax]["Lots"][lot] = 0
            vaxes[vax]["Lots"][lot] += 1
            vaxes[vax]["Total"] += 1
        print("-" * 80)
        header = "Vaccine lots"
        if self.vax:
            header += f" for vaccines matching '{self.vax}'"
        header += f" for {self.year} data."
        print(header)
        print()
        for vax in vaxes:
            print(f"{vax}:")
            for lot in sorted(
                vaxes[vax]["Lots"], key=lambda x: vaxes[vax]["Lots"][x], reverse=True
            ):
                pct = vaxes[vax]["Lots"][lot] / vaxes[vax]["Total"] * 100
                print(f"  {lot}: {vaxes[vax]['Lots'][lot]} ({pct:.2f}%)")
            print(f"Total: {vaxes[vax]['Total']}")
            print()
        print("-" * 80)

    def vax_deaths(self):
        vaxes = {}
        total = 0
        for vid in self.data:
            vax = self.data[vid]["VAX_NAME"]
            if self.vax and self.vax.lower() not in vax.lower():
                continue
            if vax not in vaxes:
                vaxes[vax] = {"Deaths": 0, "Total": 0}
            vaxes[vax]["Total"] += 1
            if self.data[vid]["DIED"] == "Y":
                vaxes[vax]["Deaths"] += 1
        print("-" * 80)
        header = "Deaths per vaccine"
        if self.vax:
            header += f" for vaccines matching '{self.vax}'"
        header += f" for {self.year} data."
        print(header)
        print()
        for vax in sorted(vaxes, key=lambda x: vaxes[x]["Deaths"], reverse=True):
            pct = vaxes[vax]["Deaths"] / vaxes[vax]["Total"] * 100
            print(f"{vax}: {vaxes[vax]['Deaths']} ({pct:0.2f}%)")
            total += vaxes[vax]["Deaths"]
        print()
        print(f"Total deaths: {total}")
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
        header += f"Minimum symptom count: {min_lim}  Minimum percent: {min_pct:.2f}%  Filters: [{', '.join(filters)}]  Dedupe: {dedupe}"
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
                    print(f"{k}: {v} ({pct:0.2f}%)")
                else:
                    other += v
            if other:
                print(
                    f"Below Threshold (Min Count:{min_lim}  Min Percent:{min_pct:0.2f}%): {other}"
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
        "https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-total-admin-rate-total"
    )


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
        help="print vaccine counts",
    )
    output_group.add_argument(
        "-d",
        "--deaths",
        default=False,
        action="store_true",
        help="print vaccine deaths",
    )
    output_group.add_argument(
        "-g",
        "--graph",
        default=False,
        action="store_true",
        help="graph number of VAERS reports",
    )
    output_group.add_argument(
        "-l",
        "--lots",
        default=False,
        action="store_true",
        help="print vaccine lots",
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
    if args.deaths:
        vaers.vax_deaths()
    if args.graph:
        graph_reports(vaers)
    if args.lots:
        vaers.vax_lots()
    if args.symptoms:
        vaers.vax_symptoms(min_lim=25, min_pct=0)
    if args.text:
        vaers.get_symptom_texts(args.text)


if __name__ == "__main__":
    main()
