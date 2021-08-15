#!/usr/bin/env python3

import sys
import json


SYMPTOMS = ["SYMPTOM1", "SYMPTOM2", "SYMPTOM3", "SYMPTOM4", "SYMPTOM5"]
FILES = ("VAERSDATA.json", "VAERSSYMPTOMS.json", "VAERSVAX.json")


class Vaers(object):
    def __init__(self, files):
        self.data = json.load(open(files[0], encoding="latin1"))
        self.symptoms = json.load(open(files[1], encoding="latin1"))
        self.vax = json.load(open(files[2], encoding="latin1"))

    def print_vaccine_types(self, ids):
        vaccines = {}
        total = len(ids)
        for i in ids:
            vaccine = self.vax[i]["VAX_NAME"]
            vaccines[vaccine] = vaccines.get(vaccine, 0) + 1
        for k, v in sorted(vaccines.items(), key=lambda x: x[1]):
            print(f"{k}: {v} ({100*v/total:.2f}%)")
        print()
        print(f"Total: {total}")

    def vax_symptoms(self, min_lim=25):
        vaxes = {}
        for vid in self.vax:
            vax = self.vax[vid]["VAX_NAME"]
            if vax not in vaxes:
                vaxes[vax] = {}
            for symptom in SYMPTOMS:
                try:
                    if self.symptoms[vid][symptom]:
                        symp_fix = self.symptoms[vid][symptom].lower()
                        vaxes[vax][symp_fix] = vaxes[vax].get(symp_fix, 0) + 1
                except KeyError:
                    print(f"{vid} is not present in the symptoms DB")
        for vax in vaxes:
            print(vax)
            for k, v in sorted(vaxes[vax].items(), key=lambda x: x[1], reverse=True):
                if v >= min_lim:
                    print(f"{k}: {v}")
            print()

    def get_symptom_texts(self, text='inappropriate age'):
        for vid in self.symptoms:
            for symptom in SYMPTOMS:
                if text in self.symptoms[vid][symptom]:
                    try:
                        print(f"{self.data[vid]['SYMPTOM_TEXT']}")
                    except KeyError:
                        print(f"{vid} not in Data DB")
                    print()


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
    for k, v in sorted(count.items(), key=lambda x: x[1]):
        print(f"{k}: {v} ({100*v/total:.2f}%)")
    print()
    print(f"Total: {total}")


def print_fully_vaxed():
    print(
        """https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-total-admin-rate-total
13aug2021
Unknown2dose 94606 (0.05%)
Janssen 13634118 (8.13%)
Moderna 64113369 (38.23%)
Pfizer 89857077 (53.58%)
Total 167699170
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
    count_key(vaers.vax, "VAX_NAME", match="COVID")


def main():
    try:
        year = sys.argv[1]
    except IndexError:
        year = '2021'
    vaers = Vaers([year + x for x in FILES])
    vaers.vax_symptoms()
    #vaers.get_symptom_texts('uphoric mood')

if __name__ == "__main__":
    main()
