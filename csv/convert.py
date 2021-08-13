#!/usr/bin/env python3

import csv
import json
import pandas

def csv_to_json(base_path):
    csv_file = f'{base_path}.csv'
    json_file = f'{base_path}.json'
    data = pandas.read_csv(csv_file, encoding='latin1', low_memory=False)
    data.to_json(json_file)
    
def make_json(base_path, key="VAERS_ID"):
    csv_file_path = f'{base_path}.csv'
    json_file_path = f'{base_path}.json'
    data = {}
      
    with open(csv_file_path, encoding='latin1') as csvf: 
        csv_reader = csv.DictReader(csvf)
        for row in csv_reader: 
            #data.append(row)
            data[row[key]] = row
    with open(json_file_path, 'w', encoding='latin1') as jsonf: 
        jsonf.write(json.dumps(data, indent=4))

def main():
    make_json('2021VAERSDATA')
    make_json('2021VAERSSYMPTOMS')
    make_json('2021VAERSVAX')

if __name__ == '__main__':
    main()
