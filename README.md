1. Download the data from https://vaers.hhs.gov/data/datasets.html
2. Unzip the files into csv/
3. Run `convert.py` on the extracted csv files

    Ex: `./convert.py 2021VAERS*csv`

4. `mv` the converted json files to the base directory
5. Run `process.py` specifying at least one output option.

    Ex: `./process.py -y 2021 -s`
