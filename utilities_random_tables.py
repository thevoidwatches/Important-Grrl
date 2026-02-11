# Utilty functions for using .csv files for weighted tables.
# Files must haev a tableweight column containing numerical weights, but can otherwise be constructed with any information.
# The weights represent how many chances a given row has to be pulled.

import csv
import random
from pathlib import Path

#Takes the file name of a csv table and loads it into memory as a tuple, with one entry being a list of the rows in the table and the other being a list of the weights for those rows.
def buildTable(filename):
    items = []
    weights = []
    with open(filename, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            item = {}
            for column in row:
                if column != 'tableweight':
                    item[column] = row[column]
            items.append(item)
            weights.append(int(row['tableweight']))
    return (items, weights)

#Loads every csv from a folder using builtTable, with each separate file being an entry in a single dictionary.
def load_files(folder):
    ret = {}
    folderpath = Path(folder)
    filenames = [p.name for p in folderpath.iterdir() if p.is_file() and p.suffix == ".csv"]
    for filename in filenames:
        key = filename.replace(".csv","")
        ret[key] = buildTable(f"{folder}/{filename}")
    return ret

#Takes one or more tuples which are outputs of buildTable() and randomly rolls from them.
def weightedTable(*tables):
    items = []
    weights = []
    for table in tables:
        items += table[0]
        weights += table[1]
    return random.choices(items, weights=weights, k=1)[0]