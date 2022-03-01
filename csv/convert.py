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


# TODO: Convert the symptoms into a list
def vaers_dump(files):
    def get_csv_handle(fname):
        return csv.DictReader(open(fname, encoding="latin1"))

    data_fname, symptoms_fname, vax_fname = files
    json_file_path = data_fname.replace("DATA.csv", ".json")
    if not json_file_path.endswith("json"):
        json_file_path += ".json"
    VAX_FIELDS = [
        "VAX_TYPE",
        "VAX_MANU",
        "VAX_LOT",
        "VAX_DOSE_SERIES",
        "VAX_ROUTE",
        "VAX_SITE",
        "VAX_NAME",
    ]
    data = {}
    pk = "VAERS_ID"
    datafh = get_csv_handle(data_fname)
    symptomsfh = get_csv_handle(symptoms_fname)
    vaxfh = get_csv_handle(vax_fname)
    for row in datafh:
        row_id = row[pk]
        data[row_id] = row
        data[row_id]["SYMPTOMVERSION"] = ""
        data[row_id]["SYMPTOMS"] = []
        for vax_field in VAX_FIELDS:
            data[row_id][vax_field] = ""
    for row in symptomsfh:
        row_id = row[pk]
        try:
            data[row_id]["SYMPTOMVERSION"] = row["SYMPTOMVERSION1"]
            for symp in ["SYMPTOM" + str(x) for x in range(1, 6)]:
                if row[symp]:
                    data[row_id]["SYMPTOMS"].append(row[symp])
        except KeyError:
            print(f"WARN: {row_id} is not present in data!", file=sys.stderr)
    for row in vaxfh:
        row_id = row[pk]
        try:
            for vax_field in VAX_FIELDS:
                data[row_id][vax_field] = row[vax_field]
        except KeyError:
            print(f"WARN: {row_id} is not present in data!", file=sys.stderr)
    with open(json_file_path, "w", encoding="latin1") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def main():
    vaers_dump(sys.argv[1:])


if __name__ == "__main__":
    main()
