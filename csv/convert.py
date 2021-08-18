#!/usr/bin/env python3

import csv
import json
import pandas
import sys


def make_json_pandas(base_path):
    csv_file = f"{base_path}.csv"
    json_file = f"{base_path}.json"
    data = pandas.read_csv(csv_file, encoding="latin1", low_memory=False)
    data.to_json(json_file)


def make_json(csv_file_path, key="VAERS_ID"):
    json_file_path = csv_file_path.replace(".csv", ".json")
    if not json_file_path.endswith(".json"):
        json_file_path += ".json"
    data = {}

    with open(csv_file_path, encoding="latin1") as csvf:
        csv_reader = csv.DictReader(csvf)
        for row in csv_reader:
            # data.append(row)
            data[row[key]] = row
    with open(json_file_path, "w", encoding="latin1") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


# def vaers_dump(data, symptoms, vax):
#    def get_csv_handle(fh):
#        return csv.DictReader(open(fname, encoding='latin1'))
#    data = {}
#    pk = 'VAERS_ID'
#    with get_csv_handle(data) as datafh:
#


def main():
    for fname in sys.argv[1:]:
        make_json(fname)


if __name__ == "__main__":
    main()
