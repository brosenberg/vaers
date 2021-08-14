#!/usr/bin/env python3

import json


class Vaers(object):
    def __init__(self, dataf, symptomsf, vaxf):
        # self.data = json.load(open(dataf, encoding='latin1'))
        self.symptoms = json.load(open(symptomsf, encoding="latin1"))
        self.vax = json.load(open(vaxf, encoding="latin1"))

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


def main():
    vaers = Vaers("2021VAERSDATA.json", "2021VAERSSYMPTOMS.json", "2021VAERSVAX.json")
    # count_key(vaers.vax, "VAX_NAME", match="COVID")
    stroke_ids = find_keys_ret_id(
        vaers.symptoms,
        ["SYMPTOM1", "SYMPTOM2", "SYMPTOM3", "SYMPTOM4", "SYMPTOM5"],
        "stroke",
    )
    vaers.print_vaccine_types(stroke_ids)


if __name__ == "__main__":
    main()
